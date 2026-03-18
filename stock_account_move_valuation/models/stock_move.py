import logging

from odoo import models, fields
from odoo.tools.float_utils import float_is_zero, float_repr, float_round, float_compare

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        # Init a dict that will group the moves by valuation type, according to `move._is_valued_type`.
        valued_moves = {valued_type: self.env['stock.move'] for valued_type in self._get_valued_types()}
        for move in self:
            if not move.product_id.categ_id.is_create_journal_on_move:
                continue
            if move.state == 'done':
                continue
            if float_is_zero(move.quantity, precision_rounding=move.product_uom.rounding):
                continue
            if not any(move.move_line_ids.mapped('picked')):
                continue
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move

        res = super()._action_done(cancel_backorder=cancel_backorder)

        # '_action_done' might have deleted some exploded stock moves
        valued_moves = {value_type: moves.exists() for value_type, moves in valued_moves.items()}

        for move in res:
            for valued_type in self._get_valued_types():
                if getattr(move, '_is_%s' % valued_type)():
                    valued_moves[valued_type] |= move

        # Create the valuation layers in batch by calling `moves._create_valued_type_svl`.
        for valued_type in self._get_valued_types():
            todo_valued_moves = valued_moves[valued_type]
            if todo_valued_moves:
                todo_valued_moves._create_stock_move_account_moves(valued_type)

        return res
    
    def _create_stock_move_account_moves(self, valued_type):
        """Create accounting entries for done moves that lack them.

        This mirrors Odoo 18 behavior by ensuring real-time valued moves
        generate journal entries after validation.
        """
        moves = self.filtered(
            lambda m: m.state == "done"
            and m.product_id.is_storable
            and m.company_id
            and m.product_id.categ_id.property_valuation == "real_time"
            and m.value > 0
        )
        if not moves:
            return

        product_accounts = self.product_id._get_product_accounts()
        if valued_type == 'in':
            debit_acc = product_accounts['stock_variation']
            credit_acc = product_accounts['stock_valuation']
        else:
            debit_acc = product_accounts['stock_valuation']
            credit_acc = product_accounts['stock_variation']
        
        move_vals = self._prepare_account_move_vals(credit_acc.id, debit_acc.id)
        move = self.env['account.move'].sudo().create(move_vals)
        move.sudo().action_post()
        return move
        
    
    
    def _prepare_account_move_vals(self, credit_account_id, debit_account_id):
        self.ensure_one()
        journal_id = self.product_id.categ_id.property_stock_journal.id

        move_ids = self._prepare_account_move_line_vals(credit_account_id, debit_account_id)
        if self.env.context.get('force_period_date'):
            date = self.env.context.get('force_period_date')
        else:
            date = fields.Date.context_today(self)
        return {
            'journal_id': journal_id,
            'line_ids': move_ids,
            'partner_id': self.partner_id.id,
            'name': self.picking_id.name,
            'date': date,
            'ref': self.picking_id.origin,
            'move_type': 'entry',
            'is_storno': self.env.context.get('is_returned') and self.company_id.account_storno,
            'company_id': self.company_id.id,
            'branch_id': self.branch_id.id,
        }
    
    def _prepare_account_move_line_vals(self, credit_account_id, debit_account_id):
        value = self._get_aml_value()
        return [(0, 0,{
            'account_id': credit_account_id,
            'name': self.reference + ' - ' + self.product_id.name,
            'debit': 0,
            'credit': value,
            'product_id': self.product_id.id,
            'branch_id': self.branch_id.id,
        }), (0, 0, {
            'account_id': debit_account_id,
            'name': self.reference + ' - ' + self.product_id.name,
            'debit': value,
            'credit': 0,
            'product_id': self.product_id.id,
            'branch_id': self.branch_id.id,
        })]