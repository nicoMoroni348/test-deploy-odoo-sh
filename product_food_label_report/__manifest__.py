# -*- coding: utf-8 -*-
{
    "name": "Product Food Label Report",
    "version": "1.0.0",
    "summary": "Rótulo alimenticio A6 para productos con advertencias e info nutricional",
    "author": "UTN",
    "license": "LGPL-3",
    "depends": ["product", "uom", "mrp", "stock", "product_expiry"],
    "data": [
        "security/ir.model.access.csv",
        "models/product_food_label_data.xml",
        "views/food_label_warning_views.xml",
        "views/product_views.xml",
        "reports/report.xml",
        "reports/product_food_label_templates.xml",
    ],
    'sequence': -1100,
    'application': False,
    'installable': True,
    'auto_install': False,
}


