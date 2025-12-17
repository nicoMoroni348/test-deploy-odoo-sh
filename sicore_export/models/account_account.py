# -*- coding: utf-8 -*-

from odoo import models, fields


class AccountAccount(models.Model):
    _inherit = 'account.account'

    sicore_export_type = fields.Selection([
        ('none', 'No exportar'),
        ('retention', 'Retenciones'),
        ('perception', 'Percepciones'),
        ('fuel', 'Combustibles'),
    ], string='Exportación SICORE',
       default='none',
       required=True,
       help='Define si los apuntes de esta cuenta se exportan a SICORE y de qué tipo')
