# -*- coding: utf-8 -*-
"""
Generador de TXT para Combustibles SICORE

Formato de salida (separado por punto y coma):
C;RAZON_PROVEEDOR;CUIT_PROVEEDOR;5;001;NUMERO_COMPROBANTE;FECHA;RAZON_CLIENTE;CUIT_CLIENTE;3;IMPORTE

Ejemplo real:
C;BARALE S.A. - 306;30543035064;5;001;2300041130;27092025;TOSTADERO MANICOP S.R.L.;30707753303;3;44680,51
"""

import re
from odoo import models, _  # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


class FuelGenerator(models.Model):
    _name = 'sicore.fuel.generator'
    _inherit = 'sicore.abstract.generator'
    _description = 'Generador de Combustibles SICORE'

    def _get_model_name(self):
        """Combustibles se generan desde apuntes contables de facturas de compra"""
        return 'account.move.line'

    def _get_separator(self):
        """Combustibles usa separador punto y coma"""
        return ';'

    def _get_field_specs(self):
        """
        Especificación de campos según formato SICORE para Combustibles
        Formato CSV con separador punto y coma
        
        Ejemplo: C;BARALE S.A. - 306;30543035064;5;001;2300041130;27092025;TOSTADERO MANICOP S.R.L.;30707753303;3;44680,51
        
        Campos:
        1. codigo_registro: 'C' (constante)
        2. razon_social_proveedor: Nombre del proveedor de combustible
        3. cuit_proveedor: CUIT del proveedor (11 dígitos)
        4. codigo_impuesto: '5' (constante - TODO: validar)
        5. codigo_regimen: '001' (constante - TODO: validar)
        6. numero_comprobante: Número de la factura de compra
        7. fecha_comprobante: Fecha en formato DDMMYYYY
        8. razon_social_cliente: Nombre de la empresa (quien compra)
        9. cuit_cliente: CUIT de la empresa (11 dígitos)
        10. codigo_constante: '3' (constante - TODO: validar significado)
        11. importe: Monto con coma decimal
        """
        return {
            # Campo 1: Código de registro - Siempre 'C'
            # TODO: Validar con cliente qué significa este código y si puede variar
            'codigo_registro': {
                'type': 'text',
                'required': True,
            },
            # Campo 2: Razón social del proveedor de combustible
            'razon_social_proveedor': {
                'type': 'text',
                'required': True,
            },
            # Campo 3: CUIT del proveedor (11 dígitos sin guiones)
            'cuit_proveedor': {
                'type': 'text',
                'required': True,
            },
            # Campo 4: Código de impuesto - Siempre '5'
            # TODO: Validar con cliente si este valor puede cambiar y de dónde viene
            'codigo_impuesto': {
                'type': 'text',
                'required': True,
            },
            # Campo 5: Código de régimen - Siempre '001'
            # TODO: Validar con cliente si este valor puede cambiar y de dónde viene
            'codigo_regimen': {
                'type': 'text',
                'required': True,
            },
            # Campo 6: Número de comprobante (solo números)
            'numero_comprobante': {
                'type': 'text',
                'required': True,
            },
            # Campo 7: Fecha del comprobante (DDMMYYYY sin separadores)
            'fecha_comprobante': {
                'type': 'date',
                'format': 'DDMMYYYY',
                'required': True,
            },
            # Campo 8: Razón social del cliente (empresa del sistema)
            'razon_social_cliente': {
                'type': 'text',
                'required': True,
            },
            # Campo 9: CUIT del cliente (empresa del sistema, 11 dígitos)
            'cuit_cliente': {
                'type': 'text',
                'required': True,
            },
            # Campo 10: Código constante - Siempre '3'
            # TODO: Validar con cliente qué representa este código
            'codigo_constante': {
                'type': 'text',
                'required': True,
            },
            # Campo 11: Importe con coma decimal
            'importe': {
                'type': 'decimal_comma',
                'decimals': 2,
                'required': True,
            },
        }

    def _get_records_domain(self, wizard):
        """
        Filtra apuntes contables de combustible según:
        - Cuenta con sicore_export_type = 'fuel' (CRITERIO PRINCIPAL)
        - Movimientos en estado posted o paid
        - Diario con exportación habilitada (no presupuesto, o ambos)
        - Rango de fechas
        - Opcional: filtros de diario/partner
        
        NOTA: El tipo de movimiento puede variar (facturas, pagos, asientos, etc.)
        pero la cuenta contable es la que determina si es combustible o no.
        """
        
        domain = [
            # La cuenta contable determina si es combustible
            ('account_id.sicore_export_type', '=', 'fuel'),
            ('move_id.state', 'in', ['posted', 'paid']),
            # ('move_id.move_type', 'in', ['in_invoice', 'in_refund']),  # SOLO facturas de proveedor
            ('company_id', '=', wizard.company_id.id),
            # El diario debe permitir exportación (no ser solo presupuesto)
            ('journal_id.sicore_export_type', '!=', 'budget'),
        ]
        
        # Filtro de fechas
        if wizard.date_from:
            domain.append(('date', '>=', wizard.date_from))
        if wizard.date_to:
            domain.append(('date', '<=', wizard.date_to))
        
        # Filtro de diarios
        if hasattr(wizard, 'journal_ids') and wizard.journal_ids:
            domain.append(('journal_id', 'in', wizard.journal_ids.ids))
        
        # Filtro de partners
        if hasattr(wizard, 'partner_ids') and wizard.partner_ids:
            domain.append(('partner_id', 'in', wizard.partner_ids.ids))
        
        return domain

    def _get_record_values(self, move_line, wizard=None):
        """
        Extrae valores del apunte contable para generar línea CSV según formato SICORE Combustibles
        
        Formato: C;RAZON_PROVEEDOR;CUIT_PROVEEDOR;5;001;NUMERO_COMP;FECHA;RAZON_CLIENTE;CUIT_CLIENTE;3;IMPORTE
        
        El proveedor es el partner del apunte (quien vende combustible)
        El cliente es la empresa del sistema (quien compra combustible)
        
        Usa parámetros del wizard para valores configurables en lugar de hardcodeados.
        """
        self._validate_move_line(move_line)
        
        partner = move_line.partner_id  # Proveedor de combustible
        move = move_line.move_id
        company = self.env.company  # Empresa del sistema (cliente)
        
        # Datos del PROVEEDOR (quien vende combustible)
        cuit_proveedor = self._get_clean_cuit(partner)
        razon_social_proveedor = partner.name or ''
        
        # Datos del CLIENTE (empresa del sistema, quien compra)
        cuit_cliente = self._get_clean_cuit(company.partner_id)
        razon_social_cliente = company.name or ''
        
        # Número de comprobante (solo números)
        numero_comp = re.sub(r'[^0-9]', '', move.name or '')
        
        # Importe = valor absoluto del balance del apunte
        importe = abs(move_line.balance)
        
        # Usar valores del wizard si están disponibles, sino usar defaults
        codigo_registro = wizard.adv_combustible_codigo_registro if wizard else 'C'
        codigo_impuesto = wizard.adv_combustible_codigo_impuesto if wizard else '5'
        codigo_regimen = wizard.adv_combustible_codigo_regimen if wizard else '001'
        codigo_constante = wizard.adv_combustible_codigo_constante if wizard else '3'
        
        return {
            # Campo 1: Código de registro
            'codigo_registro': codigo_registro,
            
            # Campo 2: Razón social del proveedor
            'razon_social_proveedor': razon_social_proveedor,
            
            # Campo 3: CUIT del proveedor
            'cuit_proveedor': cuit_proveedor,
            
            # Campo 4: Código de impuesto
            'codigo_impuesto': codigo_impuesto,
            
            # Campo 5: Código de régimen
            'codigo_regimen': codigo_regimen,
            
            # Campo 6: Número de comprobante
            'numero_comprobante': numero_comp,
            
            # Campo 7: Fecha del comprobante (DDMMYYYY)
            'fecha_comprobante': move.invoice_date or move.date,
            
            # Campo 8: Razón social del cliente (empresa del sistema)
            'razon_social_cliente': razon_social_cliente,
            
            # Campo 9: CUIT del cliente (empresa del sistema)
            'cuit_cliente': cuit_cliente,
            
            # Campo 10: Código constante
            'codigo_constante': codigo_constante,
            
            # Campo 11: Importe
            'importe': importe,
        }

    def apply_padding(self, value, spec):
        """
        Para CSV no aplicamos padding, solo retornamos el valor
        Override del método padre
        """
        return str(value) if value is not None else ''

    # ===========================
    # Métodos de validación
    # ===========================

    def _validate_move_line(self, move_line):
        """
        Valida que el apunte contable tenga toda la configuración requerida
        """
        errors = []
        
        # Validar partner (proveedor de combustible)
        if not move_line.partner_id:
            errors.append(_("PARTNER FALTANTE: El apunte contable '%s' no tiene partner (proveedor) asociado.") % move_line.move_id.name)
        else:
            # Validar CUIT del proveedor
            if not move_line.partner_id.vat:
                errors.append(
                    _("CUIT PROVEEDOR FALTANTE: El proveedor '%s' (ID: %s) no tiene CUIT configurado. "
                      "Abre el contacto del proveedor > Pestaña 'Ventas y Compras' > Campo 'TAX ID (CUIT)' > Ingresa el CUIT") %
                    (move_line.partner_id.name, move_line.partner_id.id)
                )
        
        # Validar CUIT de la empresa (cliente)
        company = self.env.company
        if not company.partner_id.vat:
            errors.append(
                _("CUIT EMPRESA FALTANTE: La empresa '%s' no tiene CUIT configurado. "
                  "Menú 'Ajustes' > 'Compañías' > Selecciona '%s' > Pestaña 'Información General' > Campo 'TAX ID (CUIT)' > Ingresa el CUIT") %
                (company.name, company.name)
            )
        
        # Validar que la cuenta sea de tipo fuel
        if move_line.account_id.sicore_export_type != 'fuel':
            errors.append(
                _("CUENTA NO CONFIGURADA: El apunte contable '%s' usa la cuenta '%s' que no está configurada como Combustible. "
                  "Abre la cuenta contable '%s' > Pestaña 'Configuración' > Campo 'Tipo Exportación SICORE' > Selecciona 'Combustible'") %
                (move_line.move_id.name, move_line.account_id.name, move_line.account_id.name)
            )
        
        if errors:
            raise ValidationError(" | ".join(errors))

    def _get_clean_cuit(self, partner):
        """Limpia el CUIT removiendo guiones y espacios"""
        vat = partner.vat or ''
        if vat:
            vat = re.sub(r'[^0-9]', '', str(vat))
        return vat
