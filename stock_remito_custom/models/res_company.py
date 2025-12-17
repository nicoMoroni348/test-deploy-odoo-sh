# -*- coding: utf-8 -*-
"""
Extensión del modelo res.company para agregar campos de imágenes
y datos fiscales para el remito personalizado.
"""

from odoo import models, fields  # type: ignore


class ResCompany(models.Model):
    """
    Extensión del modelo res.company para agregar imágenes y datos fiscales del remito.
    """
    _inherit = 'res.company'

    # ============================================================
    # IMÁGENES DEL REMITO
    # ============================================================
    
    remito_watermark = fields.Binary(
        string='Marca de Agua Remito',
        help='Imagen que se mostrará como marca de agua en el fondo del remito. '
             'Se recomienda una imagen PNG con fondo transparente.',
        attachment=True,
    )
    
    remito_footer_image = fields.Binary(
        string='Logo Footer Remito',
        help='Imagen del logo de la imprenta o similar que aparece en el pie del remito.',
        attachment=True,
    )
    
    remito_barcode_image = fields.Binary(
        string='Imagen Código de Barras',
        help='Imagen del código de barras que aparece en el pie del remito. '
             'Se recomienda una imagen PNG o JPG con el código de barras generado externamente.',
        attachment=True,
    )

    # ============================================================
    # INFORMACIÓN FISCAL - ENCABEZADO DEL REMITO
    # ============================================================
    
    remito_subtitle = fields.Char(
        string='Subtítulo Remito',
        help='Subtítulo que aparece debajo del nombre de la empresa (ej: PRODUCTOS PARA COPETIN)',
        default='',
    )
    
    remito_fiscal_type = fields.Char(
        string='Tipo Responsable Fiscal',
        help='Tipo de responsable fiscal (ej: IVA RESPONSABLE INSCRIPTO)',
        default='',
    )
    
    remito_cm_number = fields.Char(
        string='C.M. (Código de Afiliación)',
        help='Código de Matrícula o Afiliación (ej: C.M. Nº 30-70775330-3)',
        default='',
    )
    
    remito_gross_income = fields.Char(
        string='Ingresos Brutos',
        help='Número de ingresos brutos (ej: Ingresos Brutos C.M. Nº 30-70775330-3)',
        default='',
    )
    
    remito_activity_start = fields.Char(
        string='Inicio de Actividades',
        help='Fecha de inicio de actividades (ej: Inicio de Actividades: 02/08/01)',
        default='',
    )
    
    remito_address = fields.Char(
        string='Dirección Remito',
        help='Dirección que aparece en el encabezado del remito',
        default='',
    )
    
    remito_phone = fields.Char(
        string='Teléfono/Fax Remito',
        help='Teléfono y Fax que aparecen en el encabezado del remito',
        default='',
    )
    
    remito_email = fields.Char(
        string='E-mail Remito',
        help='Correo electrónico que aparece en el encabezado del remito',
        default='',
    )
    
    remito_letter = fields.Selection(
        selection=[
            ('R', 'R - Remito'),
            ('X', 'X - Remito X'),
        ],
        string='Letra del Remito',
        default='R',
        help='Letra del tipo de comprobante para los remitos',
    )

    # ============================================================
    # INFORMACIÓN FISCAL - PIE DEL REMITO
    # ============================================================
    
    # Líneas del footer - Datos de la imprenta (4 líneas)
    remito_footer_line1 = fields.Char(
        string='Footer Línea 1 (CUIT e Ing. Brutos)',
        help='Primera línea del footer con CUIT e Ing. Brutos (ej: C.U.I.T. Nº: 30-70802408-9 - Ing. Brutos Nº 211.22095-3)',
        default='',
    )
    
    remito_footer_line2 = fields.Char(
        string='Footer Línea 2 (Hab. Estab.)',
        help='Segunda línea del footer (ej: Hab. Nº de Hab. Estab. 2740842)',
        default='',
    )
    
    remito_footer_line3 = fields.Char(
        string='Footer Línea 3 (Dirección y Tel)',
        help='Tercera línea del footer (ej: Mitre 575 - Tel./Fax: 03571- 413732)',
        default='',
    )
    
    remito_footer_line4 = fields.Char(
        string='Footer Línea 4 (Localidad)',
        help='Cuarta línea del footer (ej: 5850 - Rio Tercero - Cba.)',
        default='',
    )
    
    remito_print_date = fields.Char(
        string='Fecha Impresión',
        help='Fecha de impresión del remito (ej: 03/06/2025)',
        default='',
    )
    
    remito_printing_doc_line1 = fields.Char(
        string='Doc. Impresión Línea 1',
        help='Primera línea del documento de impresión (ej: 0001-00044001 al)',
        default='',
    )
    
    remito_printing_doc_line2 = fields.Char(
        string='Doc. Impresión Línea 2',
        help='Segunda línea del documento de impresión (ej: 001-00045500)',
        default='',
    )
    
    remito_cai = fields.Char(
        string='C.A.I. (Código de Autorización)',
        help='Código de Autorización AFIP para los remitos',
        default='',
    )
    
    remito_cai_valid_from = fields.Date(
        string='Fecha Validez Inicio C.A.I.',
        help='Fecha a partir de la cual es válido el C.A.I.',
    )
    
    remito_cai_valid_to = fields.Date(
        string='Fecha Validez Fin C.A.I.',
        help='Fecha hasta la cual es válido el C.A.I.',
    )
