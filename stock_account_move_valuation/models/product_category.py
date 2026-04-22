import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ProductCategory(models.Model):
    _inherit = 'product.category'

    is_create_journal_on_move = fields.Boolean(string='Create Journal on Move', default=False)

    property_stock_account_input_categ_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Input Account',
        ondelete='restrict',
        check_company=True,
        help="Interim account used as the debit side when creating a vendor bill from a PO (goods received but not yet billed). Mirrors Odoo 18 stock input account behavior.",
    )
    property_stock_account_output_categ_id = fields.Many2one(
        comodel_name='account.account',
        string='Stock Output Account',
        ondelete='restrict',
        check_company=True,
        help="Interim account used as the credit side for COGS entries on customer invoices from a SO (goods delivered but not yet invoiced). Mirrors Odoo 18 stock output account behavior.",
    )