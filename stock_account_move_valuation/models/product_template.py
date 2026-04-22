import logging

from odoo import models

_logger = logging.getLogger(__name__)


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_accounts(self):
        """Extend product accounts with stock_input and stock_output from product category.

        Mirrors Odoo 18 behavior:
        - stock_input  → debit side of PO vendor bill / picking receipt entry
        - stock_output → credit side of SO customer invoice COGS / picking delivery entry
        Falls back to stock_variation when the category field is not set.
        """
        accounts = super()._get_product_accounts()
        categ = self.categ_id

        stock_input = categ.property_stock_account_input_categ_id
        stock_output = categ.property_stock_account_output_categ_id
        fallback = accounts.get('stock_variation')

        accounts['stock_input'] = stock_input or fallback
        accounts['stock_output'] = stock_output or fallback

        return accounts
