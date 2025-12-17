# -*- coding: utf-8 -*-

# Catálogos SICORE
from . import sicore_tax_code
from . import sicore_regime_code
from . import sicore_document_type

# Modelos principales
from . import sicore_export_log
from .generators import abstract_sicore_generator
from .generators import perception_generator
from .generators import retention_generator
from .generators import fuel_generator

# Extensiones de modelos Odoo
from . import res_partner
from . import account_journal
from . import account_account
from . import account_tax
