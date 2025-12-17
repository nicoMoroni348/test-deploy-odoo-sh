# -*- coding: utf-8 -*-
{
    'name': 'SICORE Export',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Exportación de TXT para SICORE',
    'description': """
        Módulo para generar archivos TXT según formato SICORE de AFIP
        ================================================================
        
        Funcionalidades:
        - Exportación de Percepciones (desde facturas de clientes)
        - Exportación de Retenciones (desde pagos a proveedores)
        - Exportación de Combustibles (desde pagos a proveedores con cuentas específicas)
        - Validación de campos según especificación SICORE
        - Logs de exportación con trazabilidad
        - Soporte multiempresa
        - Control de acceso por grupos (User/Manager)
    """,
    'author': 'UTN',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'l10n_ar',
        'mail',
    ],
    'data': [
        # Security
        'security/sicore_export_security.xml',
        'security/ir.model.access.csv',
        
        # Data - Catálogos SICORE (se carga primero)
        'data/sicore_tax_codes.xml',
        'data/sicore_regime_codes.xml',
        'data/sicore_document_types.xml',
        
        # Views
        'views/sicore_export_log_views.xml',
        'views/sicore_catalog_views.xml',
        'views/res_partner_views.xml',
        'views/account_journal_views.xml',
        'views/account_account_views.xml',
        'views/account_tax_views.xml',
        'wizards/sicore_export_wizard_views.xml',
        
        # Menus
        'views/sicore_export_menus.xml',
    ],
    'installable': True,
    'application': False,
    'sequence': -100,
    'auto_install': False,
}
