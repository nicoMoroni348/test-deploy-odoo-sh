# -*- coding: utf-8 -*-

import base64
from odoo import models, fields, api, _  # type: ignore
from odoo.exceptions import UserError, ValidationError  # type: ignore


class SicoreExportWizard(models.TransientModel):
    _name = 'sicore.export.wizard'
    _description = 'Wizard de Exportación SICORE'

    # ============================================================
    # CAMPOS PRINCIPALES
    # ============================================================
    
    export_type = fields.Selection([
        ('perception', 'Percepciones'),
        ('retention', 'Retenciones'),
        ('fuel', 'Combustibles'),
    ], string='Tipo de Exportación', required=True, default='retention')
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company
    )
    
    # ============================================================
    # FILTROS
    # ============================================================
    
    date_from = fields.Date(
        string='Fecha Desde',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1)  # Primer día del mes
    )
    
    date_to = fields.Date(
        string='Fecha Hasta',
        required=True,
        default=fields.Date.today
    )
    
    journal_ids = fields.Many2many(
        'account.journal',
        string='Diarios',
        domain="[('company_id', '=', company_id), ('sicore_export_type', '!=', 'budget')]",
        help='Dejar vacío para incluir todos los diarios (excepto presupuestos)'
    )
    
    partner_regime = fields.Selection([
        ('all', 'Todos'),
        ('general', 'Régimen General'),
        ('simplified', 'Régimen Simplificado'),
    ], string='Régimen', default='all')
    
    # ============================================================
    # VISTA PREVIA
    # ============================================================
    
    preview_data = fields.Text(
        string='Vista Previa',
        compute='_compute_preview_data',
        help='Resumen de registros que se exportarán'
    )
    
    records_count = fields.Integer(
        string='Cantidad de Registros',
        compute='_compute_preview_data'
    )
    
    total_retention_amount_preview = fields.Monetary(
        string='Monto Total Retenido/Percibido',
        currency_field='currency_id',
        compute='_compute_preview_data',
        help='Suma estimada de los importes de retenciones/percepciones'
    )
    
    total_transaction_amount_preview = fields.Monetary(
        string='Monto Total de Transacciones',
        currency_field='currency_id',
        compute='_compute_preview_data',
        help='Suma estimada de los importes de los comprobantes'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    # ============================================================
    # CONFIGURACIÓN AVANZADA - RETENCIONES/PERCEPCIONES
    # ============================================================
    
    adv_codigo_operacion = fields.Char(
        string='Código de Operación',
        default='1',
        help='Valor usado en campo de código de operación (por defecto: 1)'
    )
    
    adv_codigo_condicion = fields.Char(
        string='Código de Condición',
        default='01',
        help='Valor usado en campo de código de condición (por defecto: 01)'
    )
    
    adv_retencion_sujetos_suspendidos = fields.Char(
        string='Retención Sujetos Suspendidos',
        default='0',
        help='Indica si hay retención a sujetos suspendidos (por defecto: 0)'
    )
    
    adv_porcentaje_exclusion = fields.Char(
        string='Porcentaje de Exclusión',
        default='000000',
        help='Porcentaje de exclusión en retenciones (por defecto: 000000)'
    )
    
    adv_numero_certificado_original = fields.Char(
        string='Número Certificado Original',
        default='00000000000000',
        help='Número de certificado original (por defecto: 14 ceros)'
    )
    
    adv_fecha_emision_boletin = fields.Char(
        string='Fecha de Emisión del Boletín',
        default='0000000000',
        help='Fecha de emisión del boletín en percepciones (por defecto: 10 ceros)'
    )
    
    # ============================================================
    # CONFIGURACIÓN AVANZADA - COMBUSTIBLES
    # ============================================================
    
    adv_combustible_codigo_registro = fields.Char(
        string='Código de Registro (Combustible)',
        default='C',
        help='Código de registro para combustibles (por defecto: C)'
    )
    
    adv_combustible_codigo_impuesto = fields.Char(
        string='Código de Impuesto (Combustible)',
        default='5',
        help='Código de impuesto para combustibles (por defecto: 5)'
    )
    
    adv_combustible_codigo_regimen = fields.Char(
        string='Código de Régimen (Combustible)',
        default='001',
        help='Código de régimen para combustibles (por defecto: 001)'
    )
    
    adv_combustible_codigo_constante = fields.Char(
        string='Código Constante (Combustible)',
        default='3',
        help='Código constante para combustibles (por defecto: 3)'
    )
    
    # ============================================================
    # ONCHANGES
    # ============================================================
    
    @api.onchange('company_id')
    def _onchange_company(self):
        """Limpiar filtros al cambiar empresa"""
        self.journal_ids = False
    
    @api.onchange('date_from', 'date_to')
    def _onchange_dates(self):
        """Validar rango de fechas"""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise UserError(_("La fecha 'Desde' no puede ser mayor a la fecha 'Hasta'"))
    
    # ============================================================
    # COMPUTE METHODS
    # ============================================================
    
    @api.depends('export_type', 'date_from', 'date_to', 'journal_ids', 'partner_regime', 'company_id')
    def _compute_preview_data(self):
        """Genera vista previa de registros usando read_group para performance"""
        for wizard in self:
            if not wizard.export_type:
                wizard.preview_data = _("Seleccione un tipo de exportación")
                wizard.records_count = 0
                wizard.total_retention_amount_preview = 0.0
                wizard.total_transaction_amount_preview = 0.0
                continue
            
            try:
                generator = wizard._get_generator()
                domain = generator._get_records_domain(wizard)
                model_name = generator._get_model_name()
                
                records_count = self.env[model_name].search_count(domain)
                wizard.records_count = records_count
                
                # Calcular totales estimados
                total_retention = 0.0
                total_transaction = 0.0
                
                if records_count > 0:
                    records = self.env[model_name].search(domain)
                    for record in records:
                        # Para retenciones/percepciones: balance es el importe retenido
                        if hasattr(record, 'balance'):
                            total_retention += abs(record.balance)
                            # Intentar obtener el importe del comprobante desde el asiento
                            if hasattr(record, 'move_id') and record.move_id:
                                total_transaction += abs(record.move_id.amount_total or 0.0)
                        elif hasattr(record, 'amount'):
                            total_retention += abs(record.amount)
                
                wizard.total_retention_amount_preview = total_retention
                wizard.total_transaction_amount_preview = total_transaction
                
                if records_count == 0:
                    wizard.preview_data = _("No se encontraron registros con los filtros aplicados")
                    continue
                # Formatear preview básico con saltos de línea
                preview_lines = [
                    "=== RESUMEN DE EXPORTACIÓN ===",
                    f"Tipo: {dict(wizard._fields['export_type'].selection)[wizard.export_type]}",
                    f"Período: {wizard.date_from} a {wizard.date_to}",
                    f"Total Registros: {records_count}",
                ]
                
                # Intentar obtener estadísticas con read_group
                try:
                    if model_name == 'account.payment':
                        group_field = 'partner_id'
                        amount_field = 'amount'
                    elif model_name == 'account.move.line':
                        group_field = 'partner_id'
                        amount_field = 'balance'
                    else:  # account.move
                        group_field = 'partner_id'
                        amount_field = 'amount_total'
                    
                    stats = self.env[model_name].read_group(
                        domain=domain,
                        fields=[f'{amount_field}:sum', 'id:count_distinct'],
                        groupby=[group_field],
                        lazy=False
                    )
                    
                    if stats:
                        preview_lines.extend([
                            "",
                            "=== DETALLE POR PARTNER ===",
                        ])
                        
                        for stat in stats[:10]:  # Mostrar solo top 10
                            partner_name = stat.get(group_field, ['', 'Sin partner'])[1]
                            total = stat.get(f'{amount_field}', 0)
                            # Intentar obtener el conteo de diferentes formas
                            count = stat.get('id', stat.get(f'{group_field}_count', stat.get('__count', 0)))
                            preview_lines.append(
                                f"• {partner_name}: {count} registros - Total: ${total:,.2f}"
                            )
                        
                        if len(stats) > 10:
                            preview_lines.append(f"\n... y {len(stats) - 10} partners más")
                    
                except Exception:
                    preview_lines.append("")
                    preview_lines.append("(Detalle por partner no disponible)")
                
                wizard.preview_data = '\n'.join(preview_lines)
                
            except Exception as e:
                wizard.preview_data = _("Error generando vista previa: %s") % str(e)
                wizard.records_count = 0
    
    # ============================================================
    # MÉTODOS AUXILIARES
    # ============================================================
    
    def _get_generator(self):
        """Retorna instancia del generador según tipo de exportación"""
        generator_map = {
            'perception': 'sicore.perception.generator',
            'retention': 'sicore.retention.generator',
            'fuel': 'sicore.fuel.generator',
        }
        
        model_name = generator_map.get(self.export_type)
        if not model_name:
            raise UserError(_("Tipo de exportación no válido"))
        
        return self.env[model_name]
    
    # ============================================================
    # ACCIÓN PRINCIPAL
    # ============================================================
    
    def action_generate_export(self):
        """Genera el archivo TXT, lo descarga y crea log en segundo plano"""
        import logging
        import traceback
        self.ensure_one()
        
        _logger = logging.getLogger(__name__)
        
        if self.records_count == 0:
            raise UserError(_("No hay registros para exportar con los filtros seleccionados"))
        
        try:
            # Obtener generador
            generator = self._get_generator()
            
            # Generar contenido TXT
            txt_content, success_count, errors_log, state, total_retention, total_transaction = generator.generate_txt(self)
            
            if not txt_content:
                error_msg = "No se pudo generar el archivo TXT - Contenido vacío o ningún registro procesado correctamente"
                _logger.error(f"[SICORE] {error_msg}")
                raise UserError(_(error_msg))
            
            # Crear log en segundo plano
            log = self.env['sicore.export.log'].create({
                'name': f"{dict(self._fields['export_type'].selection)[self.export_type]} - {fields.Date.today()}",
                'export_type': self.export_type,
                'company_id': self.company_id.id,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'records_count': success_count,
                'total_retention_amount': total_retention,
                'total_transaction_amount': total_transaction,
                'file_content': base64.b64encode(txt_content.encode('utf-8')),
                'state': state,
                'error_log': errors_log if errors_log else False,
                'journal_ids': [(6, 0, self.journal_ids.ids)] if self.journal_ids else False,
                'partner_regime': self.partner_regime,
            })
            
            # Generar nombre de archivo
            export_type_name = dict(self._fields['export_type'].selection)[self.export_type].lower().replace(' ', '_')
            today = fields.Date.today().strftime('%Y%m%d')
            filename = f"sicore_{export_type_name}_{today}.txt"
            
            # Mensaje de éxito en el sistema
            if errors_log:
                log.message_post(
                    body=_("Exportación completada con advertencias:\n%s") % errors_log,
                    message_type='notification'
                )
            
            # Retornar acción para descargar archivo directamente
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/sicore.export.log/{log.id}/file_content/{filename}?download=true',
                'target': 'self',
            }
            
        except ValidationError as e:
            error_msg = f"Error de validación: {str(e)}"
            _logger.error(f"[SICORE] {error_msg}")
            raise UserError(_(error_msg))
        except UserError as e:
            # Re-lanzar errores de usuario sin modificar
            raise e
        except Exception as e:
            error_details = traceback.format_exc()
            error_msg = f"Error inesperado durante generación:\n{str(e)}\n\nDetalles técnicos:\n{error_details}"
            _logger.error(f"[SICORE] {error_msg}")
            
            # Crear log de error
            try:
                self.env['sicore.export.log'].create({
                    'name': f"ERROR - {dict(self._fields['export_type'].selection)[self.export_type]} - {fields.Date.today()}",
                    'export_type': self.export_type,
                    'company_id': self.company_id.id,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'records_count': 0,
                    'state': 'error',
                    'error_log': error_msg,
                })
            except:
                pass  # Si también falla crear el log, al menos tenemos el traceback
            
            raise UserError(_(error_msg))
