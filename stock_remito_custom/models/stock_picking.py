# -*- coding: utf-8 -*-
"""
Extensión del modelo stock.picking para el Remito Personalizado.
Este módulo agrega campos fiscales y lógica de validación para la generación
de remitos valorizados que cumplan con los requisitos de Manicop.
"""

from odoo import models, fields, api, _  # type: ignore
from odoo.exceptions import UserError  # type: ignore


def normalize_text(text):
    """
    Normaliza texto reemplazando tildes y caracteres especiales.
    Útil para evitar problemas de encoding en PDFs.
    
    Args:
        text: Texto a normalizar
        
    Returns:
        str: Texto sin tildes ni caracteres especiales
    """
    if not text:
        return text
    
    # Diccionario de reemplazos
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N',
        'ü': 'u', 'Ü': 'U',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o',
        'Ä': 'A', 'Ë': 'E', 'Ï': 'I', 'Ö': 'O',
        '°': 'º',
        '–': '-', '—': '-',
        '"': '"', '"': '"',
        ''': "'", ''': "'",
    }
    
    result = str(text)
    for old_char, new_char in replacements.items():
        result = result.replace(old_char, new_char)
    
    return result


class StockPicking(models.Model):
    """
    Extensión del modelo stock.picking para agregar campos fiscales
    y validaciones necesarias para la impresión del remito personalizado.
    
    Campos agregados:
    - remito_cai: Número de CAI para el remito
    - remito_cai_due_date: Fecha de vencimiento del CAI
    - remito_number: Número de remito (formato XXXX-XXXXXXXX)
    - remito_letter: Letra del remito (R, X, etc.)
    """
    _inherit = 'stock.picking'

    # === Campos Fiscales para el Remito ===
    remito_number = fields.Char(
        string='Número de Remito',
        help='Número del remito en formato XXXX-XXXXXXXX',
        tracking=True,
        copy=False,
    )
    
    remito_observations = fields.Text(
        string='Observaciones',
        help='Observaciones adicionales para el remito',
    )
    
    remito_son_pesos = fields.Char(
        string='Son Pesos',
        compute='_compute_remito_son_pesos',
        help='Monto total en letras',
    )

    @api.depends('move_ids_without_package', 'move_ids_without_package.product_id')
    def _compute_remito_son_pesos(self):
        """
        Calcula el monto total del remito en letras.
        Usa el precio de lista del producto (lst_price).
        """
        for picking in self:
            total = 0.0
            if picking.picking_type_code == 'outgoing':
                for move in picking.move_ids_without_package:
                    # Usar precio de lista del producto
                    price = move.product_id.lst_price or 0.0
                    total += move.quantity * price
            picking.remito_son_pesos = self._amount_to_text(total) if total > 0 else ''

    def _amount_to_text(self, amount):
        """
        Convierte un monto numérico a texto en español.
        
        Args:
            amount: Monto a convertir
            
        Returns:
            str: Monto en letras (ej: "Mil doscientos treinta y cuatro con 56/100")
        """
        # Diccionarios para conversión (sin tildes para evitar problemas de encoding)
        unidades = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
        decenas = ['', 'diez', 'veinte', 'treinta', 'cuarenta', 'cincuenta', 
                   'sesenta', 'setenta', 'ochenta', 'noventa']
        especiales = {
            11: 'once', 12: 'doce', 13: 'trece', 14: 'catorce', 15: 'quince',
            16: 'dieciseis', 17: 'diecisiete', 18: 'dieciocho', 19: 'diecinueve',
            21: 'veintiuno', 22: 'veintidos', 23: 'veintitres', 24: 'veinticuatro',
            25: 'veinticinco', 26: 'veintiseis', 27: 'veintisiete', 28: 'veintiocho',
            29: 'veintinueve'
        }
        centenas = ['', 'ciento', 'doscientos', 'trescientos', 'cuatrocientos',
                    'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos']

        def _numero_a_letras(n):
            """Convierte un número entero a letras."""
            if n == 0:
                return 'cero'
            if n == 100:
                return 'cien'
            if n in especiales:
                return especiales[n]
            
            resultado = ''
            
            # Millones (sin tilde: millon en lugar de millón)
            if n >= 1000000:
                millones = n // 1000000
                if millones == 1:
                    resultado += 'un millon '
                else:
                    resultado += _numero_a_letras(millones) + ' millones '
                n = n % 1000000
            
            # Miles
            if n >= 1000:
                miles = n // 1000
                if miles == 1:
                    resultado += 'mil '
                else:
                    resultado += _numero_a_letras(miles) + ' mil '
                n = n % 1000
            
            # Centenas
            if n >= 100:
                resultado += centenas[n // 100] + ' '
                n = n % 100
            
            # Decenas y unidades
            if n > 0:
                if n in especiales:
                    resultado += especiales[n]
                elif n < 10:
                    resultado += unidades[n]
                else:
                    decena = n // 10
                    unidad = n % 10
                    if unidad == 0:
                        resultado += decenas[decena]
                    else:
                        resultado += decenas[decena] + ' y ' + unidades[unidad]
            
            return resultado.strip()

        # Separar parte entera y decimal
        parte_entera = int(amount)
        parte_decimal = int(round((amount - parte_entera) * 100))
        
        texto = _numero_a_letras(parte_entera)
        texto = texto[0].upper() + texto[1:] if texto else 'Cero'
        texto += f' con {parte_decimal:02d}/100'
        
        return texto

    def _normalize_text(self, text):
        """
        Método de instancia para normalizar texto.
        Wrapper de la función normalize_text para uso en vistas QWeb.
        
        Args:
            text: Texto a normalizar
            
        Returns:
            str: Texto sin tildes ni caracteres especiales
        """
        return normalize_text(text)

    def _get_remito_line_data(self):
        """
        Obtiene los datos de las líneas para el remito valorizado.
        Todos los textos se normalizan para evitar problemas de encoding.
        El precio se obtiene del producto (lst_price).
        
        Returns:
            list: Lista de diccionarios con los datos de cada línea
        """
        self.ensure_one()
        lines_data = []
        
        for move in self.move_ids_without_package:
            # Usar precio de lista del producto
            price_unit = move.product_id.lst_price or 0.0
            # quantity = move.quantity # TODO: Validar con cliente
            quantity = move.product_uom_qty
            subtotal = quantity * price_unit
            
            # Obtener nombre del producto sin código
            product_name = move.product_id.name or ''
            
            # Obtener número de lote del move
            lot_number = ''
            if move.lot_ids:
                lot_number = move.lot_ids[0].name or ''
            
            # Crear descripción con producto y lote
            if lot_number:
                description_custom = f"{product_name} Lote: {lot_number}"
            else:
                description_custom = f"{product_name} Lote: --"
            
            # Normalizar textos para evitar problemas de encoding en PDF
            lines_data.append({
                'move': move,
                'product': move.product_id,
                'code': normalize_text(move.product_id.default_code or ''),
                'quantity': quantity,
                'description': normalize_text(description_custom),
                'price_unit': price_unit,
                'subtotal': subtotal,
            })
        
        return lines_data

    def _get_remito_total(self):
        """
        Calcula el total del remito valorizado.
        Usa el precio de lista del producto (lst_price).
        
        Returns:
            float: Monto total del remito
        """
        self.ensure_one()
        total = 0.0
        for move in self.move_ids_without_package:
            price = move.product_id.lst_price or 0.0
            # total += move.quantity * price # TODO: Validar con cliente
            total += move.product_uom_qty * price

        return total

    def action_print_custom_remito(self):
        """
        Acción para imprimir el remito personalizado.
        Soporta múltiples registros para impresión desde vista lista.
        
        Validaciones por cada picking:
        - El picking debe ser de tipo 'outgoing' (entrega a cliente)
        - Debe tener líneas de producto
        
        Returns:
            dict: Acción para generar el reporte PDF
            
        Raises:
            UserError: Si alguna validación falla
        """
        # Validar cada picking del recordset
        for picking in self:
            # Validar que sea un picking de salida
            if picking.picking_type_code != 'outgoing':
                raise UserError(_(
                    'Solo se pueden generar remitos para entregas de salida (a clientes). '
                    'El documento "%s" es de tipo "%s".'
                ) % (picking.name, picking.picking_type_id.name))
            
            # Validar que haya líneas
            if not picking.move_ids_without_package:
                raise UserError(_(
                    'El documento "%s" no tiene líneas de producto para generar el remito.'
                ) % picking.name)
        
        # Todo validado, retornar acción del reporte para todos los pickings
        return self.env.ref('stock_remito_custom.action_report_remito').report_action(self)
    
    def get_company_logo_base64(self):
        """
        Obtiene el logo de la compañía en formato base64 para el reporte.
        
        Returns:
            str: Logo en formato base64 o False si no existe
        """
        self.ensure_one()
        return self.company_id.logo if self.company_id else False
