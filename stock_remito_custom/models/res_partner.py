# -*- coding: utf-8 -*-
"""
Extensión del modelo res.partner para agregar campos de cliente
para el remito personalizado.
"""

from odoo import models, fields  # type: ignore


class ResPartner(models.Model):
    """
    Extensión del modelo res.partner para agregar campos de cliente del remito.
    """
    _inherit = 'res.partner'

    # ============================================================
    # CAMPOS DEL CLIENTE PARA REMITO
    # ============================================================
    
    customer_number = fields.Char(
        string='Número de Cliente',
        help='Número de cliente para identificación en remitos y documentos',
        default='',
    )
    
    sale_condition = fields.Char(
        string='Condición de Venta',
        help='Condición de venta del cliente (ej: CUENTA CORRIENTE.)',
        default='',
    )
