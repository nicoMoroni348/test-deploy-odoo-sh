# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AccountJournal(models.Model):
    _inherit = 'account.journal'
    
    sicore_export_type = fields.Selection([
        ('real', 'Facturas Reales'),
        ('budget', 'Presupuestos'),
        ('both', 'Ambos'),
    ], string='Tipo Exportación SICORE', 
       default='real',
       help='Define si las facturas/pagos de este diario deben exportarse a SICORE')
    
    # Campo computed para compatibilidad
    is_budget_journal = fields.Boolean(
        string='Es Diario de Presupuesto',
        compute='_compute_is_budget_journal',
        store=True,
        help='Calculado automáticamente desde Tipo Exportación SICORE'
    )
    
    @api.depends('sicore_export_type')
    def _compute_is_budget_journal(self):
        """Determina si es diario de presupuesto según tipo exportación"""
        for journal in self:
            journal.is_budget_journal = (journal.sicore_export_type == 'budget')
