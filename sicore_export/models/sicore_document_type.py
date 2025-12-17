# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SicoreDocumentType(models.Model):
    _name = 'sicore.document.type'
    _description = 'Catálogo de Tipos de Documento SICORE'
    _order = 'code'
    
    code = fields.Char(
        string='Código',
        required=True,
        size=2,
        help='Código de tipo de documento según tabla AFIP SICORE'
    )
    
    name = fields.Char(
        string='Tipo de Documento',
        required=True,
        translate=True
    )
    
    l10n_ar_doc_type_id = fields.Many2one(
        'l10n_latam.identification.type',
        string='Tipo Doc Argentina',
        help='Mapeo con tipo de documento de localización argentina'
    )
    
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'El código de tipo de documento debe ser único.')
    ]
