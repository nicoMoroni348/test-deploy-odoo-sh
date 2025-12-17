# -*- coding: utf-8 -*-

import re
import unicodedata
from odoo import models, fields, _  # type: ignore
from odoo.exceptions import ValidationError  # type: ignore


class AbstractSicoreGenerator(models.AbstractModel):
    _name = 'sicore.abstract.generator'
    _description = 'Generador Abstracto SICORE'

    # ============================================================
    # MÉTODOS ABSTRACTOS (Implementar en clases hijas)
    # ============================================================

    def _get_field_specs(self):
        """
        Debe retornar diccionario con especificación de campos SICORE
        Ejemplo:
        {
            'codigo_comprobante': {
                'position': (1, 2),
                'length': 2,
                'type': 'integer',
                'padding': 'left',
                'fill_char': '0',
                'required': True,
            },
            ...
        }
        """
        raise NotImplementedError("Debe implementar _get_field_specs()")

    def _get_records_domain(self, wizard):
        """Debe retornar domain para buscar registros a exportar"""
        raise NotImplementedError("Debe implementar _get_records_domain()")

    def _get_record_values(self, record, wizard=None):
        """
        Debe retornar diccionario con valores del record según specs
        Ahora recibe el wizard para acceder a la configuración avanzada
        Ejemplo: {'codigo_comprobante': '07', 'fecha_emision': date, ...}
        """
        raise NotImplementedError("Debe implementar _get_record_values()")

    def _get_separator(self):
        """Retorna separador de campos ('' para posición fija, ';' para CSV, etc.)"""
        return ''  # Por defecto posición fija

    # ============================================================
    # VALIDACIONES GENÉRICAS
    # ============================================================

    def validate_cuit(self, cuit):
        """
        Valida CUIT argentino con dígito verificador
        Retorna CUIT limpio (solo números) o lanza ValidationError
        """
        if not cuit:
            raise ValidationError(_("CUIT es requerido"))
        
        # Limpiar CUIT (quitar guiones y espacios)
        cuit_clean = re.sub(r'[^0-9]', '', str(cuit))
        
        if len(cuit_clean) != 11:
            raise ValidationError(_("CUIT debe tener 11 dígitos. CUIT: %s") % cuit)
        
        # Validar dígito verificador
        base = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        aux = 0
        
        for i in range(10):
            aux += int(cuit_clean[i]) * base[i]
        
        aux = 11 - (aux % 11)
        
        if aux == 11:
            aux = 0
        elif aux == 10:
            aux = 9
        
        if aux != int(cuit_clean[10]):
            raise ValidationError(_("CUIT inválido (dígito verificador incorrecto). CUIT: %s") % cuit)
        
        return cuit_clean

    def sanitize_text(self, text, max_length=None):
        """
        Sanitiza texto para SICORE:
        - Quita acentos
        - Convierte a mayúsculas
        - Elimina caracteres especiales
        - Trunca si excede max_length
        """
        if not text:
            return ''
        
        text = str(text)
        
        # Quitar acentos
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ASCII', 'ignore').decode('ASCII')
        
        # Mayúsculas
        text = text.upper()
        
        # Permitir solo alfanuméricos, espacios, guiones y puntos
        # TODO: Validar con cliente qué caracteres especiales deben permitirse en el TXT
        text = re.sub(r'[^A-Z0-9 \-\.]', '', text)
        
        # Truncar si es necesario
        if max_length and len(text) > max_length:
            text = text[:max_length]
        
        return text

    def format_date(self, date_value, date_format='DD/MM/YYYY'):
        """
        Formatea fecha según formato SICORE
        date_format: 'DD/MM/YYYY', 'DDMMYYYY', etc.
        """
        if not date_value:
            return ''
        
        if isinstance(date_value, str):
            # Ya es string, intentar parsear
            try:
                date_value = fields.Date.from_string(date_value)
            except:
                return date_value
        
        # Convertir según formato
        if date_format == 'DD/MM/YYYY':
            return date_value.strftime('%d/%m/%Y')
        elif date_format == 'DDMMYYYY':
            return date_value.strftime('%d%m%Y')
        elif date_format == 'YYYY-MM-DD':
            return date_value.strftime('%Y-%m-%d')
        else:
            return date_value.strftime(date_format.replace('DD', '%d').replace('MM', '%m').replace('YYYY', '%Y'))

    def format_decimal(self, value, decimals=2, remove_separator=True, use_comma=True):
        """
        Formatea decimal para SICORE
        - decimals: cantidad de decimales
        - remove_separator: si True, retorna entero sin punto (ej: 1234 para 12.34)
        - use_comma: si True, usa coma como separador decimal (formato SICORE - siempre True por defecto)
        """
        if value is None or value == '':
            value = 0
        
        try:
            value = float(value)
        except:
            raise ValidationError(_("Valor decimal inválido: %s") % value)
        
        if remove_separator:
            # Retornar como entero (multiplicar por 10^decimals)
            return str(int(round(value * (10 ** decimals))))
        else:
            # Formatear con coma como separador decimal (formato SICORE estándar)
            formatted = f"{value:.{decimals}f}"
            return formatted.replace('.', ',')

    def format_integer(self, value):
        """Formatea entero"""
        if value is None or value == '':
            value = 0
        
        try:
            return str(int(value))
        except:
            raise ValidationError(_("Valor entero inválido: %s") % value)

    # ============================================================
    # PADDING Y FORMATEO DE CAMPOS
    # ============================================================

    def apply_padding(self, value, spec):
        """
        Aplica padding a valor según especificación
        spec debe contener: length, padding ('left'/'right'), fill_char
        """
        value_str = str(value) if value is not None else ''
        length = spec.get('length', len(value_str))
        fill_char = spec.get('fill_char', ' ')
        padding = spec.get('padding', 'right')
        
        # Truncar si excede longitud
        if len(value_str) > length:
            value_str = value_str[:length]
        
        # Aplicar padding
        if padding == 'left':
            return value_str.rjust(length, fill_char)
        else:  # right
            return value_str.ljust(length, fill_char)

    def validate_and_format_field(self, field_name, value, spec):
        """
        Valida y formatea un campo según su especificación
        Retorna valor formateado o lanza ValidationError
        """
        # 1. Validar requerido
        if spec.get('required') and not value and value != 0:
            raise ValidationError(_("Campo '%s' es requerido") % field_name)
        
        # 2. Formatear según tipo
        field_type = spec.get('type', 'text')
        
        try:
            if field_type == 'integer':
                value = self.format_integer(value)
            elif field_type in ('decimal', 'decimal_comma'):
                # Ambos tipos usan coma por defecto (formato SICORE estándar)
                decimals = spec.get('decimals', 2)
                value = self.format_decimal(value, decimals, remove_separator=False)
            elif field_type == 'date':
                date_format = spec.get('format', 'DD/MM/YYYY')
                value = self.format_date(value, date_format)
            elif field_type == 'text':
                max_len = spec.get('length')
                value = self.sanitize_text(value, max_len)
            elif field_type == 'cuit':
                value = self.validate_cuit(value)
            else:
                value = str(value) if value is not None else ''
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(_("Error formateando campo '%s': %s") % (field_name, str(e)))
        
        # 3. Validación custom
        if 'validation' in spec:
            validation_fn = spec['validation']
            if not validation_fn(value):
                raise ValidationError(_("Validación falló para campo '%s'") % field_name)
        
        # 4. Aplicar padding
        value = self.apply_padding(value, spec)
        
        return value

    # ============================================================
    # GENERACIÓN DE TXT
    # ============================================================

    def format_line(self, record, wizard=None):
        """
        Genera una línea del TXT según especificaciones
        Retorna string con la línea formateada
        """
        specs = self._get_field_specs()
        values = self._get_record_values(record, wizard)
        separator = self._get_separator()
        
        line_parts = []
        errors = []
        
        for field_name, spec in specs.items():
            try:
                value = values.get(field_name)
                formatted_value = self.validate_and_format_field(field_name, value, spec)
                line_parts.append(formatted_value)
            except ValidationError as e:
                errors.append(str(e))
        
        if errors:
            raise ValidationError(_("Errores en registro:\n%s") % '\n'.join(errors))
        
        return separator.join(line_parts)

    def generate_txt(self, wizard):
        """
        Genera contenido TXT completo
        Retorna tupla: (txt_content, records_count, errors_log, state, total_retention_amount, total_transaction_amount)
        """
        import logging
        import traceback
        _logger = logging.getLogger(__name__)
        
        model_name = self._get_model_name()
        domain = self._get_records_domain(wizard)
        
        records = self.env[model_name].search(domain)
        
        lines = []
        errors_log = []
        success_count = 0
        total_retention_amount = 0.0
        total_transaction_amount = 0.0
        
        for idx, record in enumerate(records, 1):
            try:
                line = self.format_line(record, wizard)
                lines.append(line)
                success_count += 1
                
                # Calcular totales según tipo de exportación
                values = self._get_record_values(record, wizard)
                
                # Monto de retención/percepción
                retention_amount = values.get('importe_retencion') or values.get('importe') or 0.0
                if isinstance(retention_amount, (int, float)):
                    total_retention_amount += abs(retention_amount)
                
                # Monto de la transacción (comprobante)
                transaction_amount = values.get('importe_comprobante') or values.get('base_calculo') or 0.0
                if isinstance(transaction_amount, (int, float)):
                    total_transaction_amount += abs(transaction_amount)
                
            except ValidationError as e:
                error_msg = f"Error validación en registro {idx} ({record.display_name}): {str(e)}"
                _logger.warning(error_msg)
                errors_log.append(error_msg)
            except Exception as e:
                error_details = traceback.format_exc()
                error_msg = f"Error inesperado en registro {idx} ({record.display_name}): {str(e)}"
                _logger.error(f"{error_msg}\nDetalles técnicos:\n{error_details}")
                errors_log.append(error_msg)
        
        txt_content = '\n'.join(lines)
        
        # Determinar estado
        if errors_log and success_count == 0:
            state = 'error'
            _logger.error(f"[SICORE-GEN] Exportación fallida - Ningún registro procesado exitosamente")
        elif errors_log:
            state = 'warning'
        else:
            state = 'success'
        
        errors_text = '\n'.join(errors_log) if errors_log else ''
        
        return txt_content, success_count, errors_text, state, total_retention_amount, total_transaction_amount

    def _get_model_name(self):
        """Retorna nombre del modelo a exportar (implementar en hijas si es necesario)"""
        return 'account.move'
