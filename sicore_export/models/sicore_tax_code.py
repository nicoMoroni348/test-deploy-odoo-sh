# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SicoreTaxCode(models.Model):
    _name = 'sicore.tax.code'
    _description = 'Catálogo de Códigos de Impuesto SICORE'
    _order = 'code'
    
    code = fields.Char(
        string='Código',
        required=True,
        size=4,
        help='Código de impuesto según tabla AFIP SICORE'
    )
    
    name = fields.Char(
        string='Impuesto',
        required=True,
        translate=True
    )
    
    description = fields.Text(
        string='Descripción',
        translate=True
    )
    
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código de impuesto debe ser único.')
    ]
