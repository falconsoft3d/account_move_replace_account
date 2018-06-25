# coding: utf-8
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMoveReplaceAccountWizard(models.TransientModel):
    _name = 'account.move.replace.account.wizard'
    _description = 'Wizard to replace account on account move lines'

    from_account_id = fields.Many2one('account.account', 'Old Account', required=True)
    to_account_id = fields.Many2one('account.account', 'New Account', required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

    @api.constrains('from_account_id', 'to_account_id')
    def check_accounts(self):
        if self.from_account_id == self.to_account_id:
            raise ValidationError(_('Accounts can not be the same'))

    @api.constrains('date_start', 'date_end')
    def check_dates(self):
        if self.date_start > self.date_end:
            raise ValidationError(_('Date start can not be greater than Date end'))

    def replace_account(self):
        lines = self.env['account.move.line']
        to_post = self.env['account.move']
        for move in self.env['account.move'].search([('date', '>=', self.date_start), ('date', '<=', self.date_end)]):
            current_lines = move.line_ids.filtered(lambda l: l.account_id.id == self.from_account_id.id)
            if move.state == 'posted' and current_lines:
                try:
                    move.button_cancel()
                except:
                    raise ValidationError(_('%s can not be changed because %s journal is not cancellable.') % (move.name, move.journal_id.name))
                to_post += move
                lines += current_lines
            else:
                lines += current_lines
        if lines:
            lines.write({'account_id': self.to_account_id.id})
        if to_post:
            to_post.post()
        return {'type': 'ir.actions.act_window_close'}
