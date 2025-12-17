# -*- coding: utf-8 -*-

from odoo import models, fields # type: ignore


class AccountTax(models.Model):
    _inherit = 'account.tax'

    sicore_tax_code_id = fields.Many2one(
        'sicore.tax.code',
        string='Código Impuesto SICORE',
        help='Código de impuesto AFIP para exportación SICORE'
    )
    
    sicore_regime_code_id = fields.Many2one(
        'sicore.regime.code',
        string='Código Régimen SICORE',
        help='Código de régimen AFIP que define el concepto de la retención/percepción'
    )
