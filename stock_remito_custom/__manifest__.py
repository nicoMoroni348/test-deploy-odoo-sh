# -*- coding: utf-8 -*-
{
    'name': 'Remito Personalizado',
    'version': '18.0.1.0.0',
    'category': 'Inventory/Inventory',
    'summary': 'Reporte de Remito valorizado con diseño personalizado',
    'description': """
Módulo de Remito Personalizado
==============================

Este módulo genera un reporte PDF de "Remito" (Albarán) con diseño pixel-perfect
que replica el formulario preimpreso de la empresa Manicop.

Características:
----------------
* Diseño de remito dibujado digitalmente en hoja A4 blanca
* Validación estricta de precios desde la Orden de Venta vinculada
* Campos fiscales para CAI y fecha de vencimiento
* Grupo de seguridad para controlar quién puede imprimir remitos
* Marca de agua corporativa
    """,
    'author': 'UTN',
    'license': 'LGPL-3',
    'depends': [
        'stock',
        'sale_stock',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/paperformat.xml',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/stock_picking_views.xml',
        'views/report_remito.xml',
    ],
    'installable': True,
    'application': False,
    'sequence': -110,
    'auto_install': False,
}
