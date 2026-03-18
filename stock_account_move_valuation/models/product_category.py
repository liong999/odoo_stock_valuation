import logging

from odoo import models, fields
from odoo.tools.float_utils import float_is_zero, float_repr, float_round, float_compare

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_create_journal_on_move = fields.Boolean(string='Create Journal on Move', default=False)