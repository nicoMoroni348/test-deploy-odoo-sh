# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SicoreRegimeCode(models.Model):
    _name = 'sicore.regime.code'
    _description = 'Catálogo de Códigos de Régimen SICORE'
    _order = 'code'
    
    code = fields.Char(
        string='Código',
        required=True,
        size=3,
        help='Código de régimen según tabla AFIP SICORE'
    )
    
    name = fields.Char(
        string='Régimen',
        required=True,
        translate=True
    )
    
    description = fields.Text(
        string='Descripción Completa',
        translate=True
    )
    
    applies_to = fields.Selection([
        ('retention', 'Retenciones'),
        ('perception', 'Percepciones'),
        ('both', 'Ambos'),
    ], string='Aplica a', default='both', required=True)
    
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código de régimen debe ser único.')
    ]
