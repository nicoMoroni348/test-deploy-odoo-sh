# -*- coding: utf-8 -*-
import logging

from odoo import api, fields, models, _  # type: ignore
from odoo.exceptions import ValidationError  # type: ignore

_logger = logging.getLogger(__name__)


class FoodLabelWarning(models.Model):
    """
    Modelo simple para advertencias octogonales del rótulo (p. ej. EXCESO EN SODIO).
    """
    _name = "food.label.warning"
    _description = "Food Label Warning"

    name = fields.Char(string="Nombre", required=True, translate=True)
    image = fields.Binary(string="Imagen", attachment=True)
    active = fields.Boolean(string="Activo", default=True)


class ProductNutritionLine(models.Model):
    """
    Línea nutricional editable por producto.
    - name: Char (texto libre) segun requerimiento.
    - quantity_per_serving: cantidad por porción como texto (kcal, g, mg, etc.).
    - vd_percent: %VD por porción.
    """
    _name = "product.nutrition.line"
    _description = "Línea de información nutricional"
    _order = "sequence, id"

    product_tmpl_id = fields.Many2one(
        "product.template", string="Producto", ondelete="cascade", required=True, index=True
    )
    sequence = fields.Integer(string="Secuencia", default=10)

    name = fields.Char(string="Nombre", required=True)
    quantity_per_serving = fields.Char(
        string="Cantidad por porción",
        help="Texto libre para cantidad por porción, ej.: '130 kcal = 541 kJ', '10 g', '153 mg'",
    )
    vd_percent = fields.Float(string="%VD(*)", help="Porcentaje de Valor Diario por porción")

    _sql_constraints = [
        ("check_vd_percent_non_negative", "CHECK(vd_percent >= 0)", "El %VD debe ser mayor o igual a 0."),
    ]

    def _normalize_text(self, text):
        """
        Normaliza texto reemplazando tildes y ñ por caracteres sin acentos.
        Útil para evitar problemas de encoding en PDFs.
        """
        if not text:
            return text
        
        # Diccionario de reemplazos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N',
            'ü': 'u', 'Ü': 'U',
        }
        
        result = text
        for old_char, new_char in replacements.items():
            result = result.replace(old_char, new_char)
        
        return result


class ProductTemplate(models.Model):
    """
    Herencia de product.template para campos de rótulo y relación nutricional.
    Strings en español, nombres técnicos en inglés (requisito del proyecto).
    """
    _inherit = "product.template"

    # Advertencias (octógonos)
    warning_ids = fields.Many2many(
        "food.label.warning",
        "product_tmpl_food_label_warning_rel",
        "product_tmpl_id",
        "warning_id",
        string="Advertencias (octógonos)",
        help="Advertencias a imprimir en el rótulo (EXCESO EN SODIO, etc.).",
    )

    # Textos de etiqueta
    label_description = fields.Text(string="Descripción")
    label_ingredients = fields.Text(string="Ingredientes")
    label_tacc_info = fields.Text(string="TACC e información adicional")
    label_storage_mode = fields.Text(string="Conservación")
    label_manufacturing = fields.Text(string="Fabricación")
    label_address = fields.Text(string="Dirección")
    label_rne = fields.Char(string="RNE")
    label_rnpa = fields.Char(string="RNPA")

    # Porción
    serving_size_label = fields.Char(
        string="Porción",
        default="25.0 g (1 taza de té)",
        help="Ejemplo: 25.0 g (1 taza de té)"
    )

    # Relación nutricional
    nutrition_line_ids = fields.One2many(
        "product.nutrition.line", "product_tmpl_id", string="Información nutricional"
    )

    def _normalize_text(self, text):
        """
        Normaliza texto reemplazando tildes y ñ por caracteres sin acentos.
        Útil para evitar problemas de encoding en PDFs.
        """
        if not text:
            return text
        
        # Diccionario de reemplazos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N',
            'ü': 'u', 'Ü': 'U',
        }
        
        result = text
        for old_char, new_char in replacements.items():
            result = result.replace(old_char, new_char)
        
        return result

    @api.model
    def _get_company_address_lines(self, company):
        """
        Devuelve una lista con la dirección formateada de la compañía.
        Se usa como fallback si no se cargó 'Dirección' en los campos de etiqueta.
        """
        if not company or not company.partner_id:
            return []
        partner = company.partner_id
        parts = [
            partner.street or "",
            partner.street2 or "",
            f"{partner.zip or ''} {partner.city or ''}".strip(),
            partner.state_id and partner.state_id.name or "",
            partner.country_id and partner.country_id.name or "",
        ]
        return [", ".join([p for p in parts if p])]


class ProductProduct(models.Model):
    """
    Herencia de product.product para agregar el método de normalización.
    """
    _inherit = "product.product"

    def _normalize_text(self, text):
        """
        Normaliza texto reemplazando tildes y ñ por caracteres sin acentos.
        Útil para evitar problemas de encoding en PDFs.
        """
        if not text:
            return text
        
        # Diccionario de reemplazos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N',
            'ü': 'u', 'Ü': 'U',
        }
        
        result = text
        for old_char, new_char in replacements.items():
            result = result.replace(old_char, new_char)
        
        return result


class MrpProduction(models.Model):
    """
    Herencia de mrp.production para agregar campo computado de fecha.
    """
    _inherit = "mrp.production"

    date_finished_date = fields.Date(
        string="Fecha de elaboración",
        compute="_compute_date_finished_date",
        store=False,
        readonly=True,
        help="Fecha de elaboración (solo fecha, sin hora) para el rótulo alimenticio"
    )

    @api.depends('date_finished')
    def _compute_date_finished_date(self):
        """
        Convierte date_finished (Datetime) a solo fecha (Date).
        """
        for record in self:
            if record.date_finished:
                # Extraer solo la fecha del datetime
                record.date_finished_date = record.date_finished.date()
            else:
                record.date_finished_date = False


class StockLot(models.Model):
    """
    Herencia de stock.lot para agregar campo computado de fecha de vencimiento.
    Usa el campo expiration_date del módulo product_expiry.
    """
    _inherit = "stock.lot"

    expiration_date_date = fields.Date(
        string="Fecha de vencimiento",
        compute="_compute_expiration_date_date",
        store=False,
        readonly=True,
        help="Fecha de vencimiento (solo fecha, sin hora) para el rótulo alimenticio"
    )

    @api.depends('expiration_date')
    def _compute_expiration_date_date(self):
        """
        Convierte expiration_date (Datetime) a solo fecha (Date).
        """
        for record in self:
            if record.expiration_date:
                # Extraer solo la fecha del datetime
                record.expiration_date_date = record.expiration_date.date()
            else:
                record.expiration_date_date = False
