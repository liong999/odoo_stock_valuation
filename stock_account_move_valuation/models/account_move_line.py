import logging

from odoo import models

_logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_account_id(self):
        """Use stock_input account (from product category) for vendor bill lines.

        Overrides Odoo 19 default which uses stock_valuation for both PO and SO.
        When stock_input is not set on the category, falls back to stock_valuation
        through the _get_product_accounts chain.
        """
        super()._compute_account_id()
        for line in self:
            if not line.move_id.is_purchase_document():
                continue
            if not line._eligible_for_stock_account():
                continue
            if line.product_id.valuation != 'real_time':
                continue

            fiscal_position = line.move_id.fiscal_position_id
            accounts = line.with_company(line.company_id).product_id.product_tmpl_id.get_product_accounts(
                fiscal_pos=fiscal_position
            )
            stock_input = accounts.get('stock_input')
            if stock_input:
                line.account_id = stock_input
