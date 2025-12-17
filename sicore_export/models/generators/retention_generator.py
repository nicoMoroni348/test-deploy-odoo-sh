# -*- coding: utf-8 -*-

import re
from odoo import models, _  # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


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
        
        # Obtener importe del comprobante y base de cálculo
        # Para pagos con retención, necesitamos buscar la factura original
        importe_comprobante, base_calculo, factura_relacionada = self._get_invoice_amounts(move_line, move)
        
        # Obtener código de comprobante desde la FACTURA (no del asiento de pago)
        # Si hay factura relacionada, usar su tipo de documento
        # Sino, usar el tipo del asiento actual
        move_for_comprobante = factura_relacionada if factura_relacionada else move
        codigo_comprobante = self._get_codigo_comprobante(move_for_comprobante)
        
        # Limpiar número de comprobante (de la factura si existe, sino del asiento)
        numero_comp = re.sub(r'[^0-9]', '', (factura_relacionada.name if factura_relacionada else move.name) or '')
        
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
            'fecha_emision_comprobante': factura_relacionada.invoice_date if factura_relacionada else (move.invoice_date or move.date),
            'numero_comprobante': numero_comp,
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
        
        if errors:
            raise ValidationError(" | ".join(errors))

    def _get_clean_cuit(self, partner):
        """Limpia el CUIT removiendo guiones y espacios"""
        vat = partner.vat or ''
        if vat:
            vat = re.sub(r'[^0-9]', '', str(vat))
        return vat.zfill(11)  # Rellenar con ceros a la izquierda si es necesario

    def _get_codigo_comprobante(self, move):
        """
        Detecta el código de comprobante desde l10n_latam.document_type
        Si el move tiene l10n_latam_document_type_id, usa ese código.
        Sino, mapea según move_type.
        """
        # Si el asiento tiene tipo de documento de localización argentina, usarlo
        if move.l10n_latam_document_type_id and move.l10n_latam_document_type_id.code:
            return move.l10n_latam_document_type_id.code
        
        # Fallback: mapeo básico por move_type
        code_map = {
            'out_invoice': '01',  # Factura
            'in_invoice': '01',   # Factura
            'out_refund': '03',   # Nota de Crédito
            'in_refund': '03',    # Nota de Crédito
            'entry': '06',        # Recibo/Orden de Pago
        }
        
        return code_map.get(move.move_type, '06')

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
        Obtiene el importe del comprobante y base de cálculo buscando la factura relacionada.
        
        Para pagos con retención:
        1. Busca la factura que se está pagando (a través de reconciliación)
        2. Retorna el importe total de la factura y su base imponible
        
        Returns:
            tuple: (importe_comprobante, base_calculo, factura)
        """
        
        # Buscar factura relacionada a través de la reconciliación de las líneas
        # Las líneas de proveedor/cliente del pago están reconciliadas con la factura
        invoice = None
        
        # Buscar líneas del asiento que sean de tipo payable/receivable
        payable_lines = payment_move.line_ids.filtered(
            lambda l: l.account_id.account_type in ['liability_payable', 'asset_receivable']
        )
        
        for line in payable_lines:
            # Buscar la reconciliación (matched_debit_ids o matched_credit_ids)
            if line.matched_debit_ids:
                for match in line.matched_debit_ids:
                    if match.debit_move_id.move_id.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                        invoice = match.debit_move_id.move_id
                        break
            
            if not invoice and line.matched_credit_ids:
                for match in line.matched_credit_ids:
                    if match.credit_move_id.move_id.move_type in ['in_invoice', 'in_refund', 'out_invoice', 'out_refund']:
                        invoice = match.credit_move_id.move_id
                        break
            
            if invoice:
                break
        
        if invoice:
            # Importe del comprobante = total de la factura
            importe_comprobante = abs(invoice.amount_total)
            
            # Base de cálculo = subtotal sin impuestos (base imponible)
            # En Argentina, las retenciones se calculan sobre el subtotal sin IVA
            base_calculo = abs(invoice.amount_untaxed)
            
            return importe_comprobante, base_calculo, invoice
        else:            
            # Fallback: usar datos del asiento de pago
            importe_comprobante = abs(payment_move.amount_total)
            base_calculo = self._get_base_calculo(payment_move)
            
            return importe_comprobante, base_calculo, None
