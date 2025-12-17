# -*- coding: utf-8 -*-

from odoo import models, fields, api  # type: ignore


class ResPartner(models.Model):
    _inherit = 'res.partner'

    sicore_regime = fields.Selection([
        ('general', 'Régimen General'),
        ('simplified', 'Régimen Simplificado'),
    ], string='Régimen SICORE', help='Régimen para declaración SICORE')
    
    # Campo computed para compatibilidad
    is_simplified_regime = fields.Boolean(
        string='Régimen Simplificado',
        compute='_compute_is_simplified_regime',
        store=True,
        help='Calculado automáticamente desde Régimen SICORE'
    )
    
    sicore_document_type_id = fields.Many2one(
        'sicore.document.type',
        string='Tipo Documento SICORE',
        compute='_compute_sicore_document_type',
        store=True,
        help='Tipo de documento para SICORE, mapeado automáticamente desde tipo de identificación argentina'
    )
    
    @api.depends('sicore_regime')
    def _compute_is_simplified_regime(self):
        """Determina si es régimen simplificado según selección"""
        for partner in self:
            partner.is_simplified_regime = (partner.sicore_regime == 'simplified')
    
    @api.depends('l10n_latam_identification_type_id')
    def _compute_sicore_document_type(self):
        """Mapea automáticamente el tipo de documento argentino a SICORE"""
        for partner in self:
            sicore_type = False
            
            if partner.l10n_latam_identification_type_id:
                # Buscar el mapeo en sicore.document.type
                sicore_type = self.env['sicore.document.type'].search([
                    ('l10n_ar_doc_type_id', '=', partner.l10n_latam_identification_type_id.id)
                ], limit=1)
            
            partner.sicore_document_type_id = sicore_type
