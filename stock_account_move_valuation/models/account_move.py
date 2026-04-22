import logging

from odoo import models
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _stock_account_prepare_realtime_out_lines_vals(self):
        """Override to use stock_output account (from product category) for COGS credit line.

        In Odoo 19 core this uses stock_valuation for the inventory credit line on
        customer invoices. Here we redirect it to stock_output when configured on
        the product category, restoring Odoo 18 behavior. Falls back to
        stock_valuation through the _get_product_accounts chain when stock_output
        is not configured.
        """
        price_unit_prec = self.env['decimal.precision'].precision_get('Product Price')
        lines_vals_list = []

        for move in self:
            move = move.with_company(move.company_id)
            if not move.is_sale_document(include_receipts=True):
                continue

            anglo_saxon_price_ctx = move._get_anglo_saxon_price_ctx()

            for line in move.invoice_line_ids:
                if not line._eligible_for_stock_account() or line.product_id.valuation != 'real_time':
                    continue

                accounts = line.product_id.product_tmpl_id.get_product_accounts(
                    fiscal_pos=move.fiscal_position_id
                )
                stock_account = accounts.get('stock_output') or accounts['stock_valuation']
                expense_account = accounts['expense'] or move.journal_id.default_account_id
                if not stock_account or not expense_account:
                    continue

                sign = -1 if move.move_type == 'out_refund' else 1
                price_unit = line.with_context(anglo_saxon_price_ctx)._get_cogs_value()
                amount_currency = sign * line.product_uom_id._compute_quantity(
                    line.quantity, line.product_id.uom_id
                ) * price_unit

                if move.currency_id.is_zero(amount_currency) or float_is_zero(
                    price_unit, precision_digits=price_unit_prec
                ):
                    continue

                # Inventory (credit) line — uses stock_output
                lines_vals_list.append({
                    'name': line.name[:64] if line.name else '',
                    'move_id': move.id,
                    'partner_id': move.commercial_partner_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'quantity': line.quantity,
                    'price_unit': price_unit,
                    'amount_currency': -amount_currency,
                    'account_id': stock_account.id,
                    'display_type': 'cogs',
                    'tax_ids': [],
                    'cogs_origin_id': line.id,
                })

                # COGS (debit) line — uses expense account
                lines_vals_list.append({
                    'name': line.name[:64] if line.name else '',
                    'move_id': move.id,
                    'partner_id': move.commercial_partner_id.id,
                    'product_id': line.product_id.id,
                    'product_uom_id': line.product_uom_id.id,
                    'quantity': line.quantity,
                    'price_unit': -price_unit,
                    'amount_currency': amount_currency,
                    'account_id': expense_account.id,
                    'analytic_distribution': line.analytic_distribution,
                    'display_type': 'cogs',
                    'tax_ids': [],
                    'cogs_origin_id': line.id,
                })

        return lines_vals_list

