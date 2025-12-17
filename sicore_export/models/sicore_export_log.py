# -*- coding: utf-8 -*-

from odoo import models, fields, api  # type: ignore
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT  # type: ignore


class SicoreExportLog(models.Model):
    _name = 'sicore.export.log'
    _description = 'Log de Exportaciones SICORE'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'display_name'

    name = fields.Char(
        string='Referencia',
        required=True,
        default='Nueva Exportación'
    )
    
    display_name = fields.Char(
        string='Nombre',
        compute='_compute_display_name',
        store=True
    )
    
    export_type = fields.Selection([
        ('perception', 'Percepciones'),
        ('retention', 'Retenciones'),
        ('fuel', 'Combustibles'),
    ], string='Tipo de Exportación', required=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        default=lambda self: self.env.company
    )
    
    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=True,
        default=lambda self: self.env.user
    )
    
    date_from = fields.Date(
        string='Fecha Desde',
        help='Fecha de inicio del rango de exportación'
    )
    
    date_to = fields.Date(
        string='Fecha Hasta',
        help='Fecha de fin del rango de exportación'
    )
    
    records_count = fields.Integer(
        string='Registros Exportados',
        default=0
    )
    
    total_retention_amount = fields.Monetary(
        string='Monto Total Retenido/Percibido',
        currency_field='currency_id',
        help='Suma total de los importes de retenciones/percepciones aplicadas'
    )
    
    total_transaction_amount = fields.Monetary(
        string='Monto Total de Transacciones',
        currency_field='currency_id',
        help='Suma total de los importes de los comprobantes (base imponible)'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Moneda',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    file_name = fields.Char(
        string='Nombre de Archivo',
        compute='_compute_file_name',
        store=True
    )
    
    file_content = fields.Binary(
        string='Archivo TXT',
        attachment=True
    )
    
    state = fields.Selection([
        ('success', 'Exitoso'),
        ('warning', 'Con Advertencias'),
        ('error', 'Error'),
    ], string='Estado', default='success', required=True)
    
    error_log = fields.Text(
        string='Errores/Advertencias',
        help='Detalle de errores o advertencias durante la exportación'
    )
    
    # Filtros aplicados (para trazabilidad)
    journal_ids = fields.Many2many(
        'account.journal',
        string='Diarios Filtrados',
        help='Diarios incluidos en la exportación'
    )
    
    partner_regime = fields.Selection([
        ('general', 'Régimen General'),
        ('simplified', 'Régimen Simplificado'),
        ('all', 'Todos'),
    ], string='Régimen', help='Régimen filtrado en la exportación')
    
    notes = fields.Text(string='Notas')
    
    @api.depends('export_type', 'create_date', 'company_id')
    def _compute_display_name(self):
        """Genera nombre descriptivo para el log"""
        for record in self:
            type_dict = dict(self._fields['export_type'].selection)
            type_name = type_dict.get(record.export_type, 'Exportación')
            date_str = fields.Datetime.to_string(record.create_date) if record.create_date else ''
            record.display_name = f"{type_name} - {date_str[:10] if date_str else 'Sin fecha'} - {record.company_id.name if record.company_id else ''}"
    
    @api.depends('export_type', 'create_date', 'company_id')
    def _compute_file_name(self):
        """Genera nombre del archivo TXT con mismo formato que el wizard"""
        for record in self:
            if record.export_type and record.create_date:
                # Mismo formato que en wizard: sicore_<tipo>_<fecha>.txt
                type_dict = dict(self._fields['export_type'].selection)
                export_type_name = type_dict.get(record.export_type, 'export').lower().replace(' ', '_')
                date_str = fields.Date.to_string(record.create_date).replace('-', '')
                record.file_name = f"sicore_{export_type_name}_{date_str}.txt"
            else:
                record.file_name = 'sicore_export.txt'

    def action_download_file(self):
        """Acción para descargar el archivo exportado"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/sicore.export.log/{self.id}/file_content/{self.file_name}?download=true',
            'target': 'self',
        }
