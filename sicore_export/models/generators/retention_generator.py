# -*- coding: utf-8 -*-

import re
import logging
from odoo import models, _  # type: ignore
from odoo.exceptions import ValidationError  # type: ignore

_logger = logging.getLogger(__name__)


class RetentionGenerator(models.Model):
    _name = 'sicore.retention.generator'
    _inherit = 'sicore.abstract.generator'
    _description = 'Generador de Retenciones SICORE'

    def _get_model_name(self):
        """Retenciones se generan desde apuntes contables"""
        return 'account.move.line'

    def _get_field_specs(self):
        """
        Especificación de campos según formato SICORE REAL para Retenciones
        Basado en archivo: Retencion Ganancias_092025.txt
        Total: 240+ caracteres por línea
        """
        return {
            # Campo 1: Código de comprobante (2 chars)
            'codigo_comprobante': {
                'position': (1, 2),
                'length': 2,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 2: Fecha de emisión del comprobante (10 chars con formato DD/MM/YYYY)
            'fecha_emision_comprobante': {
                'position': (3, 12),
                'length': 10,
                'type': 'date',
                'format': 'DD/MM/YYYY',
                'padding': 'right',
                'fill_char': ' ',
                'required': True,
            },
            # Campo 3: Número del comprobante (16 chars)
            'numero_comprobante': {
                'position': (13, 28),
                'length': 16,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 4: Importe del comprobante (16 chars con COMA decimal)
            'importe_comprobante': {
                'position': (29, 44),
                'length': 16,
                'type': 'decimal_comma',
                'decimals': 2,
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 5: Código de impuesto (4 chars) - ej: 0217
            'codigo_impuesto': {
                'position': (45, 48),
                'length': 4,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 6: Código de regimen (3 chars) - ej: 078
            'codigo_regimen': {
                'position': (49, 51),
                'length': 3,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 7: Código de operación (1 char) - ej: 1
            'codigo_operacion': {
                'position': (52, 52),
                'length': 1,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 8: Base de cálculo (14 chars con COMA decimal)
            'base_calculo': {
                'position': (53, 66),
                'length': 14,
                'type': 'decimal_comma',
                'decimals': 2,
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 9: Fecha de emisión de la retención (10 chars DD/MM/YYYY)
            'fecha_emision_retencion': {
                'position': (67, 76),
                'length': 10,
                'type': 'date',
                'format': 'DD/MM/YYYY',
                'padding': 'right',
                'fill_char': ' ',
                'required': True,
            },
            # Campo 10: Código de condición (2 chars) - ej: 01
            'codigo_condicion': {
                'position': (77, 78),
                'length': 2,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 11: Retención practicada a sujetos suspendidos según: (1 char) - 0 o 1
            'retencion_practicada_sujetos_suspendidos': {
                'position': (79, 79),
                'length': 1,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 12: Importe de la retención (14 chars con COMA decimal)
            'importe_retencion': {
                'position': (80, 93),
                'length': 14,
                'type': 'decimal_comma',
                'decimals': 2,
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 13: Porcentaje de exclusión (6 chars)
            'porcentaje_exclusion': {
                'position': (94, 99),
                'length': 6,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': False,
            },
            # Campo 14: Fecha de publicación o de finalización de la vigencia (10 chars DD/MM/YYYY)
            'fecha_publicacion_finalizacion_vigencia': {
                'position': (100, 109),
                'length': 10,
                'type': 'date',
                'format': 'DD/MM/YYYY',
                'padding': 'right',
                'fill_char': ' ',
                'required': True,
            },
            # Campo 15: Tipo de documento del retenido (2 chars) - 80=CUIT
            'tipo_documento_retenido': {
                'position': (110, 111),
                'length': 2,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 16: Número de documento del retenido (20 chars)
            'numero_documento_retenido': {
                'position': (112, 131),
                'length': 20,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 17: Número certificado original (14 chars)
            'numero_certificado_original': {
                'position': (132, 145),
                'length': 14,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 18: Denominación del ordenante (30 chars)
            # Padding LEFT: texto alineado a la derecha, espacios a la izquierda
            'denominacion_ordenante': {
                'position': (146, 175),
                'length': 30,
                'type': 'text',
                'padding': 'left',
                'fill_char': ' ',
                'required': True,
            },
            # Campo 19: Cuit del país del retenido (11 chars)
            'cuit_pais_retenido': {
                'position': (176, 186),
                'length': 11,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            # Campo 20: Cuit del ordenante (11 chars)
            'cuit_ordenante': {
                'position': (187, 197),
                'length': 11,
                'type': 'text',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
        }

    def _get_records_domain(self, wizard):
        """
        Filtra apuntes contables según:
        - Cuenta con sicore_export_type = 'retention' (CRITERIO PRINCIPAL)
        - Movimientos en estado posted o paid
        - Diario con exportación habilitada (no presupuesto, o ambos)
        - Rango de fechas
        - Opcional: filtros de diario/partner
        
        NOTA: El tipo de movimiento puede variar (facturas, pagos, asientos, etc.)
        pero la cuenta contable es la que determina si es una retención o no.
        """
        domain = [
            ('account_id.sicore_export_type', '=', 'retention'),
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
        if wizard.journal_ids:
            domain.append(('journal_id', 'in', wizard.journal_ids.ids))
        
        # Filtro de partners
        if hasattr(wizard, 'partner_ids') and wizard.partner_ids:
            domain.append(('partner_id', 'in', wizard.partner_ids.ids))
        
        # Filtro de régimen (si aplica)
        if wizard.partner_regime and wizard.partner_regime != 'all':
            if wizard.partner_regime == 'simplified':
                domain.append(('partner_id.is_simplified_regime', '=', True))
            else:  # general
                domain.append(('partner_id.is_simplified_regime', '=', False))
        
        return domain

    def _get_record_values(self, move_line, wizard=None):
        """
        Extrae valores del apunte contable para generar línea TXT según formato SICORE real.
        Los códigos de impuesto y régimen DEBEN estar configurados en el impuesto (account.tax).
        
        Usa parámetros del wizard para valores configurables en lugar de hardcodeados.
        """
        self._validate_move_line(move_line)
        
        partner = move_line.partner_id
        move = move_line.move_id

        vat = self._get_clean_cuit(partner)
        
        # Obtener código impuesto y régimen con sistema de 3 niveles
        codigo_impuesto_raw, codigo_regimen_raw = self._get_tax_and_regime_codes(move_line)
        
        # Limpiar códigos: quitar ceros a la izquierda para que el padding funcione correctamente
        # Ejemplo: "0767" guardado en BD -> "767" -> padding lo convierte a "767" (3 chars)
        # Si no limpiamos, "0767" se truncaría a "076" que es incorrecto
        codigo_impuesto = codigo_impuesto_raw.lstrip('0') or '0' if codigo_impuesto_raw else ''
        codigo_regimen = codigo_regimen_raw.lstrip('0') or '0' if codigo_regimen_raw else ''
                
        # Obtener tipo de documento desde catálogo (80=CUIT, 86=CUIL, etc.)
        tipo_documento = self._get_document_type_code(partner)
        
        # Importe de retención = valor absoluto del balance del apunte
        importe_retencion = abs(move_line.balance)
        
        # Obtener importe del comprobante y base de cálculo desde payment + withholdings
        importe_comprobante, base_calculo, factura_relacionada = self._get_invoice_amounts(move_line, move)
        
        # Obtener código de comprobante (fijo en 06 para retenciones, configurable en wizard)
        codigo_comprobante = self._get_codigo_comprobante(move, wizard)
        
        # Número de comprobante del apunte contable
        
        # Usar valores del wizard si están disponibles, sino usar defaults
        codigo_operacion = wizard.adv_codigo_operacion if wizard else '1'
        codigo_condicion = wizard.adv_codigo_condicion if wizard else '01'
        retencion_practicada_sujetos_suspendidos = wizard.adv_retencion_sujetos_suspendidos if wizard else '0'
        porcentaje_exclusion = wizard.adv_porcentaje_exclusion if wizard else '000000'
        numero_certificado_original = wizard.adv_numero_certificado_original if wizard else '00000000000000'
        
        # TODO: Verificar si cuit_ordenante debe ser igual al cuit_pais_retenido o diferente
        cuit_ordenante = vat  # Usando mismo CUIT que el retenido por ahora
        
        return {
            'codigo_comprobante': codigo_comprobante,
            'fecha_emision_comprobante': move_line.date,
            'numero_comprobante': move_line.name,
            'importe_comprobante': importe_comprobante,
            'codigo_impuesto': codigo_impuesto,
            'codigo_regimen': codigo_regimen,
            'codigo_operacion': codigo_operacion,
            'base_calculo': base_calculo,
            'fecha_emision_retencion': move_line.date,
            'codigo_condicion': codigo_condicion,
            'retencion_practicada_sujetos_suspendidos': retencion_practicada_sujetos_suspendidos,
            'importe_retencion': importe_retencion,
            'porcentaje_exclusion': porcentaje_exclusion,
            'fecha_publicacion_finalizacion_vigencia': move_line.date,
            'tipo_documento_retenido': tipo_documento,
            'numero_documento_retenido': vat,
            'numero_certificado_original': numero_certificado_original,
            'denominacion_ordenante': partner.name or '',
            'cuit_pais_retenido': vat,
            'cuit_ordenante': cuit_ordenante,
        }

    # ===========================
    # Métodos de validación
    # ===========================

    def _validate_move_line(self, move_line):
        """
        Valida que el apunte contable tenga toda la configuración requerida.
        Sin defaults: si falta algo, error formal.
        """
        errors = []
        
        # Validar partner
        if not move_line.partner_id:
            errors.append(_("PARTNER FALTANTE: El apunte contable '%s' no tiene partner asociado.") % move_line.move_id.name)
        else:
            # Validar CUIT
            if not move_line.partner_id.vat:
                errors.append(
                    _("CUIT PARTNER FALTANTE: El partner '%s' (ID: %s) no tiene CUIT configurado. "
                      "Abre el contacto > Pestaña 'Ventas y Compras' > Campo 'TAX ID (CUIT)' > Ingresa el CUIT") %
                    (move_line.partner_id.name, move_line.partner_id.id)
                )
            
            # Validar tipo de documento
            if not move_line.partner_id.sicore_document_type_id:
                errors.append(
                    _("TIPO DE DOCUMENTO FALTANTE: El partner '%s' (ID: %s) no tiene tipo de documento SICORE configurado. "
                      "Abre el contacto > Pestaña 'Ventas y Compras' > Campo 'Tipo de Identificación SICORE' > Selecciona el tipo (DNI, CUIT, etc)") %
                    (move_line.partner_id.name, move_line.partner_id.id)
                )
        
        # Validar código de impuesto (DEBE venir del impuesto)
        tax_code = self._try_get_tax_code(move_line)
        if not tax_code:
            errors.append(
                _("CÓDIGO IMPUESTO FALTANTE: No se encontró código de impuesto SICORE para el apunte '%s'. "
                  "Menú 'Contabilidad' > 'Configuración' > 'Impuestos' > Abre el impuesto usado > Campo 'Código Impuesto SICORE' > Ingresa el código") %
                (move_line.move_id.name,)
            )
        
        # Validar código de régimen (DEBE venir del impuesto)
        regime_code = self._try_get_regime_code(move_line)
        if not regime_code:
            errors.append(
                _("CÓDIGO RÉGIMEN FALTANTE: No se encontró código de régimen SICORE para el apunte '%s'. "
                  "Menú 'Contabilidad' > 'Configuración' > 'Impuestos' > Abre el impuesto usado > Campo 'Código Régimen SICORE' > Ingresa el código") %
                (move_line.move_id.name,)
            )
        
        # Validar que el asiento contable tenga withholdings (retenciones)
        if not move_line.move_id.l10n_ar_withholding_ids:
            errors.append(
                _("RETENCIONES NO ENCONTRADAS: El asiento contable '%s' no tiene retenciones (l10n_ar_withholding_ids) asociadas. "
                  "Los apuntes de retención DEBEN estar vinculados a un asiento que contiene los datos de retención.") %
                (move_line.move_id.name,)
            )
        
        if errors:
            raise ValidationError(" | ".join(errors))

    def _get_clean_cuit(self, partner):
        """Limpia el CUIT removiendo guiones y espacios"""
        vat = partner.vat or ''
        if vat:
            vat = re.sub(r'[^0-9]', '', str(vat))
        return vat.zfill(11)  # Rellenar con ceros a la izquierda si es necesario

    def _get_codigo_comprobante(self, move, wizard=None):
        """
        Retorna el código de comprobante para exportación SICORE.
        
        Para retenciones, el código es fijo en '06' (Recibo/Orden de Pago).
        Puede ser sobreescrito desde la configuración avanzada del wizard.
        """
        # Si hay wizard y está configurado el código de comprobante avanzado, usar ese
        if wizard and hasattr(wizard, 'adv_codigo_comprobante') and wizard.adv_codigo_comprobante:
            return wizard.adv_codigo_comprobante
        
        # Default para retenciones: '06'
        return '06'

    def _get_tax_and_regime_codes(self, move_line):
        """
        Obtiene código de impuesto y régimen desde el IMPUESTO asociado al apunte.
        
        Busca en:
        1. tax_line_id: si la línea ES el resultado de un impuesto (típico para retenciones/percepciones)
        2. tax_ids: impuestos aplicados a esta línea
        
        NO hay fallback a cuenta contable ni partner - los códigos DEBEN estar en el impuesto.
        """
        tax_code = None
        regime_code = None
        
        # Primero buscar en tax_line_id (esta línea ES el resultado de un impuesto)
        # Esto es típico para líneas de retención/percepción
        if move_line.tax_line_id:
            tax = move_line.tax_line_id
            if tax.sicore_tax_code_id:
                tax_code = tax.sicore_tax_code_id.code
            if tax.sicore_regime_code_id:
                regime_code = tax.sicore_regime_code_id.code
        
        # Si no encontramos, buscar en tax_ids (impuestos aplicados a esta línea)
        if (not tax_code or not regime_code) and move_line.tax_ids:
            for tax in move_line.tax_ids:
                if not tax_code and tax.sicore_tax_code_id:
                    tax_code = tax.sicore_tax_code_id.code
                if not regime_code and tax.sicore_regime_code_id:
                    regime_code = tax.sicore_regime_code_id.code
                if tax_code and regime_code:
                    break
        
        return tax_code, regime_code

    def _try_get_tax_code(self, move_line):
        """Intenta obtener código de impuesto sin lanzar error (para validación)"""
        # Buscar en tax_line_id (línea ES el impuesto)
        if move_line.tax_line_id and move_line.tax_line_id.sicore_tax_code_id:
            return move_line.tax_line_id.sicore_tax_code_id.code
        
        # Buscar en impuestos aplicados
        if move_line.tax_ids:
            for tax in move_line.tax_ids:
                if tax.sicore_tax_code_id:
                    return tax.sicore_tax_code_id.code
        
        return None

    def _try_get_regime_code(self, move_line):
        """Intenta obtener código de régimen sin lanzar error (para validación)"""
        # Buscar en tax_line_id (línea ES el impuesto)
        if move_line.tax_line_id and move_line.tax_line_id.sicore_regime_code_id:
            return move_line.tax_line_id.sicore_regime_code_id.code
        
        # Buscar en impuestos aplicados
        if move_line.tax_ids:
            for tax in move_line.tax_ids:
                if tax.sicore_regime_code_id:
                    return tax.sicore_regime_code_id.code
        
        return None

    def _get_document_type_code(self, partner):
        """Obtiene el código de tipo de documento desde el catálogo"""
        if not partner.sicore_document_type_id:
            raise ValidationError(
                _("El partner '%s' (ID: %s) no tiene tipo de documento SICORE configurado.") %
                (partner.name, partner.id)
            )
        return partner.sicore_document_type_id.code



    def _get_move_withholding_amounts(self, move, payment):
        """
        Extrae importes desde el payment y los withholdings del asiento contable.
        
        - Importe del comprobante: payment.amount
        - Base de cálculo: suma de tax_base_amount de todos los withholdings
        
        Args:
            move: account.move record
            payment: account.payment record asociado
            
        Returns:
            tuple: (importe_comprobante, base_calculo)
        """
        # Importe del comprobante = monto total del pago
        importe_comprobante = abs(payment.amount)
        
        # Base de cálculo = suma de tax_base_amount de todos los withholdings
        base_calculo = sum(abs(w.tax_base_amount) for w in move.l10n_ar_withholding_ids)
        
        return importe_comprobante, base_calculo

    def _get_base_calculo(self, move):
        """
        Calcula la base imponible sumando las líneas de cuentas por pagar/cobrar
        del mismo asiento (excluyendo la línea de retención)
        """
        # En Odoo 18, account_type es un campo Selection directamente en account.account
        # Buscar líneas con cuentas de tipo payable/receivable
        base_lines = move.line_ids.filtered(
            lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable']
        )
                
        # Sumar el balance absoluto de estas líneas
        base_calculo = sum(abs(line.balance) for line in base_lines)
        
        return base_calculo if base_calculo > 0 else abs(move.amount_total)

    def _get_invoice_amounts(self, move_line, payment_move):
        """
        Obtiene el importe del comprobante y base de cálculo desde el pago y los withholdings.
        
        IMPORTANTE: El importe del comprobante se extrae del account.payment (payment.amount),
        mientras que la base de cálculo se extrae de los withholdings del asiento contable.
        
        Estrategia:
        1. Buscar el payment asociado al move_id (a través de move_id.payment_id)
        2. Si no encuentra, intentar con move_id.origin_payment_id
        3. Si encuentr: extraer amount del payment y tax_base_amount de withholdings
        4. Si NO encuentra en ambos: lanzar error de validación
        
        Returns:
            tuple: (importe_comprobante, base_calculo, factura_relacionada o None)
        """
        move = move_line.move_id
        
        # Buscar payment asociado al asiento contable
        payment = None
        if hasattr(move, 'payment_id') and move.payment_id:
            payment = move.payment_id
        elif hasattr(move, 'origin_payment_id') and move.origin_payment_id:
            payment = move.origin_payment_id
        
        if not payment:
            # Error: el asiento contable DEBE tener un payment asociado
            raise ValidationError(
                _("PAGO NO ENCONTRADO: El asiento contable '%s' no tiene un pago (account.payment) asociado. "
                  "Los apuntes de retención DEBEN estar vinculados a un pago.") %
                (move.name,)
            )
        
        # Extraer importes del payment + withholdings
        importe_comprobante, base_calculo = self._get_move_withholding_amounts(move, payment)
        
        # Retornar None para factura_relacionada (no la usamos en retenciones)
        return importe_comprobante, base_calculo, None
