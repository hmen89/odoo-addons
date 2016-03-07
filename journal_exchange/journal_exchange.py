# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo Module
#    Copyright (C) 2015 Grover Menacho (<http://www.grovermenacho.com>).
#    Autor: Grover Menacho
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp import models, fields, api, _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning, RedirectWarning

from lxml import etree
from openerp import SUPERUSER_ID
from datetime import datetime
import openerp
import math

def closeness(a, b):
    """Returns measure of equality (for two floats), in unit
       of decimal significant figures."""
    if a == b:
        return float("infinity")
    difference = abs(a - b)
    avg = (a + b)/2
    return math.log10( avg / difference )

class journal_exchange(models.Model):

    _name = 'journal.exchange'
    _order = 'id desc'

    @api.one
    @api.depends('journal_id', 'journal_dest_id', 'initial_amount')
    def _compute_amount(self):
        currency_obj = self.pool.get('res.currency')
        if self.journal_id and self.journal_dest_id and self.initial_amount:
            self.current_amount = currency_obj.compute(self.env.cr, self.env.uid, self.initial_currency.id, self.exchange_currency.id, self.initial_amount)
            self.current_rate = currency_obj._get_conversion_rate(self.env.cr, self.env.uid, self.initial_currency, self.exchange_currency)

    name = fields.Char(string='Reference/Description', index=True, readonly=True, default='Draft Exchange', copy=False)
    user_id = fields.Many2one('res.users', string='Exchanger', ondelete='set null', copy=False)
    confirmed_date = fields.Date(string='Confirmed Date', readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False)
    #Source
    journal_id = fields.Many2one('account.journal', string='Source Journal', ondelete='set null', select=True)
    initial_amount = fields.Float(string='Initial Amount', digits= dp.get_precision('Account'), store=True)
    initial_currency = fields.Many2one('res.currency', string='Currency Initial', ondelete='set null', select=True)
    #Destination
    journal_dest_id = fields.Many2one('account.journal', string='Destination Journal', ondelete='set null', select=True)
    exchanged_amount = fields.Float(string='Exchanged Amount', digits= dp.get_precision('Account'), store=True, copy=False)
    exchange_currency = fields.Many2one('res.currency', string='Exchange Currency', ondelete='set null', select=True)
    exchange_date = fields.Date(string='Exchange Date', readonly=True, states={'draft': [('readonly', False)]}, index=True, copy=False)
    exchanged_rate = fields.Float(string='Exchanged Rate', digits=(5,15), copy=False)
    #System
    current_rate = fields.Float(string='Current Rate', digits=(5,15), compute=_compute_amount, copy=False)
    current_amount = fields.Float(string='Current Amount', compute=_compute_amount, copy=False)
    #company_id = fields.Many2one('res.company', string='Company', readonly=True, states={'draft': [('readonly', False)]},
    #    default=lambda self: self.env['res.company']._company_default_get())

    #move_lines = fields.One2many('account.move.line', 'transfer_id', string='Move Lines',
    #    readonly=True, copy=False)
    state = fields.Selection([
            ('draft','Draft'),
            ('done','Done'),
            ('cancel','Cancelled'),
        ], string='Status', index=True, readonly=True, default='draft',copy=False)


    @api.multi
    def onchange_journal_id(self, journal_id=False, journal_dest_id=False, amount=0.0):
        journal_obj = self.pool.get('account.journal')
        currency_obj = self.pool.get('res.currency')
        company_currency = self.pool.get('res.users').browse(self.env.cr, self.env.uid, self.env.uid).company_id.currency_id
        res = {'value':{}}
        rate=0.0
        exchanged_amount=0.0
        if journal_id:
            currency_id = journal_obj.browse(self.env.cr, self.env.uid ,journal_id).currency or company_currency
            if journal_id and journal_dest_id:
                currency_dest_id = journal_obj.browse(self.env.cr, self.env.uid ,journal_dest_id).currency or company_currency
                if (currency_id and currency_dest_id and currency_id.id==currency_dest_id.id) or (not currency_id and not currency_dest_id):
                    raise Warning(_('Both journals have the same currency. You can\'t transfer this'))
                rate = currency_obj._get_conversion_rate(self.env.cr, self.env.uid, currency_id, currency_dest_id)
                exchanged_amount = currency_obj.compute(self.env.cr, self.env.uid, currency_id.id, currency_dest_id.id, amount)

            res['value'].update({'initial_currency': currency_id,
                                 'current_rate': rate,
                                 'current_amount': exchanged_amount})

        return res

    @api.multi
    def onchange_journal_dest_id(self, journal_id=False, journal_dest_id=False, amount=0.0):
        journal_obj = self.pool.get('account.journal')
        currency_obj = self.pool.get('res.currency')
        company_currency = self.pool.get('res.users').browse(self.env.cr, self.env.uid, self.env.uid).company_id.currency_id
        res = {'value':{}}
        rate=0.0
        exchanged_amount=0.0
        if journal_dest_id:
            currency_dest_id = journal_obj.browse(self.env.cr, self.env.uid ,journal_dest_id).currency or company_currency
            if journal_id and journal_dest_id:
                currency_id = journal_obj.browse(self.env.cr, self.env.uid ,journal_id).currency or company_currency
                if (currency_id and currency_dest_id and currency_id.id==currency_dest_id.id) or (not currency_id and not currency_dest_id):
                    raise Warning(_('Both journals have the same currency. You can\'t transfer this'))
                rate = currency_obj._get_conversion_rate(self.env.cr, self.env.uid, currency_id, currency_dest_id)
                exchanged_amount = currency_obj.compute(self.env.cr, self.env.uid, currency_id.id, currency_dest_id.id, amount)
            res['value'].update({'exchange_currency': currency_dest_id,
                                 'current_rate': rate,
                                 'current_amount': exchanged_amount})

        return res

    @api.multi
    def onchange_rate_exchanged(self, exchanged_rate=0.0,exchanged_amount=0.0,initial_amount=0.0):
        if initial_amount and exchanged_rate:
            if exchanged_rate>0.0 and closeness(float(exchanged_amount), float(initial_amount/exchanged_rate)) < 3:
                return {'value': {'exchanged_amount': initial_amount*exchanged_rate}}
        else:
            return {'value': {'exchanged_amount': 0.0}}

        return True

    @api.multi
    def onchange_amount_exchanged(self, exchanged_rate=0.0,exchanged_amount=0.0,initial_amount=0.0):
        if exchanged_amount and initial_amount:
            if exchanged_amount>0.0 and closeness(float(exchanged_rate), float(initial_amount/exchanged_amount)) < 3:
                return {'value': {'exchanged_rate': exchanged_amount/initial_amount}}
        else:
            return {'value': {'exchanged_rate': 0.0}}

        return True

    @api.multi
    def check_permissions(self, type=None):
        if type=='send':
            if self.env.uid in [o.id for o in self.journal_id.journal_outcome_user_ids]:
                return True
            else:
                return False
        elif type=='receive':
            if self.env.uid in [o.id for o in self.journal_dest_id.journal_income_user_ids]:
                return True
            else:
                return False
        return False

    @api.multi
    def create_exchange_move(self):
        currency_obj = self.pool.get('res.currency')
        account_move_obj=self.pool.get('account.move')
        account_move_line_obj=self.pool.get('account.move.line')
        tax_obj = self.pool.get('account.tax')

        move_id = account_move_obj.create(self.env.cr, self.env.uid, {
                    'ref' : self.name,
                    'journal_id': self.journal_id.id,
                    #'transfer_id': self.id,
                })

        #amount_exceeded = self.received_value - self.sent_value
        company_id = self.env['res.company'].browse(self.env['res.company']._company_default_get())
        company_currency = company_id.currency_id


        #Converting to company currency
        if company_currency == self.journal_id.currency or not self.journal_id.currency:
            company_initial_amount = self.initial_amount
        else:
            company_initial_amount = self.journal_id.currency.compute(self.initial_amount, company_currency)

        move_line_id = account_move_line_obj.create(self.env.cr, self.env.uid, {
            'name': self.journal_id.name,
            'account_id': self.journal_id.default_credit_account_id.id,
            'credit': ((company_initial_amount>0) and company_initial_amount) or 0.0,
            'debit': ((company_initial_amount<0) and -company_initial_amount) or 0.0,
            'move_id': move_id,
            'currency_id': self.journal_id.currency and self.journal_id.currency.id or False,
            'amount_currency': self.journal_id.currency and -self.initial_amount or 0.0,
            'date': self.exchange_date,
        })

        #Converting to company currency
        if company_currency == self.journal_dest_id.currency or not self.journal_dest_id.currency:
            company_exchanged_amount = self.exchanged_amount
        else:
            company_exchanged_amount = self.journal_dest_id.currency.compute(self.exchanged_amount,company_currency)

        counterpart_move_line_id = account_move_line_obj.create(self.env.cr, self.env.uid, {
            'name': self.journal_dest_id.name,
            'account_id': self.journal_dest_id.default_debit_account_id.id,
            'credit': ((company_exchanged_amount<0) and -company_exchanged_amount) or 0.0,
            'debit': ((company_exchanged_amount>0) and company_exchanged_amount) or 0.0,
            'move_id': move_id,
            'currency_id': self.journal_dest_id.currency and self.journal_dest_id.currency.id or False,
            'amount_currency': self.journal_dest_id.currency and self.exchanged_amount or 0.0,
            'date': self.exchange_date,
        })


        #Now we're checking the residual amount

        amount_residual = company_initial_amount - company_exchanged_amount

        if amount_residual > 0:
            account_id = company_id.expense_currency_exchange_account_id
            if not account_id:
                model, action_id = self.pool['ir.model.data'].get_object_reference(self.env.cr, self.env.uid, 'account', 'action_account_form')
                msg = _("You should configure the 'Loss Exchange Rate Account' to manage automatically the booking of accounting entries related to differences between exchange rates.")
                raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))
        elif amount_residual < 0:
            account_id = company_id.income_currency_exchange_account_id
            if not account_id:
                model, action_id = self.pool['ir.model.data'].get_object_reference(self.env.cr, self.env.uid, 'account', 'action_account_form')
                msg = _("You should configure the 'Gain Exchange Rate Account' to manage automatically the booking of accounting entries related to differences between exchange rates.")
                raise openerp.exceptions.RedirectWarning(msg, action_id, _('Go to the configuration panel'))


        move_line_exchange_residual = account_move_line_obj.create(self.env.cr, self.env.uid, {
            'name': _('residual exchange')+': '+(self.journal_dest_id.name or '/'),
            'account_id': account_id.id,
            'debit': amount_residual > 0 and amount_residual or 0.0,
            'credit': amount_residual < 0 and -amount_residual or 0.0,
            'move_id': move_id,
            'date': self.exchange_date,
        })


        return True



    @api.multi
    def confirm(self):
        if self.initial_currency == self.exchange_currency:
            raise Warning(_('Both journals have the same currency. You can\'t transfer this'))
        exchange_number = self.pool.get('ir.sequence').get(self.env.cr, self.env.uid, 'journal.exchange')
        if self.exchange_date:
            exchange_date = self.exchange_date
        else:
            exchange_date = fields.Date.context_today(self)
        self.write({'state': 'done',
                    'name': exchange_number,
                    'confirmed_date':fields.Date.context_today(self),
                    'user_id':self.env.uid,
                    'exchange_date':exchange_date})
        self.create_exchange_move()
        return True

    @api.multi
    def cancel(self):
        #Disabled because we've permission fields on journal_transfer
        #if not self.check_permissions('send'):
        #    raise osv.except_osv(_('Error!'), _('You are not allowed to cancel this transfer. Please contact your sender.'))
        self.write({'state': 'cancel'})
        #TODO: Delete account.move
        return True


    @api.multi
    def cancel(self):
        #Disabled because we've permission fields on journal_transfer
        #if not self.check_permissions('send'):
        #    raise osv.except_osv(_('Error!'), _('You are not allowed to cancel this transfer. Please contact your sender.'))
        self.write({'state': 'cancel'})
        #TODO: Delete account.move
        account_move_obj = self.pool.get('account.move')
        account_move_ids = account_move_obj.search(self.env.cr, self.env.uid, [('transfer_id','=',self.id)])

        for line in self.move_lines:
            if not line.journal_id.update_posted:
                raise osv.except_osv(_('Error!'), _('You cannot modify a posted entry of this journal.\nFirst you should set the journal to allow cancelling entries.'))
        if account_move_ids:
            self.env.cr.execute('UPDATE account_move '\
                       'SET state=%s '\
                       'WHERE id IN %s', ('draft', tuple(account_move_ids),))
            account_move_obj.unlink(self.env.cr, self.env.uid, account_move_ids)


        return True



    @api.multi
    def unlink(self):
        for transfer in self:
            if transfer.state not in ('draft', 'cancel'):
                raise Warning(_('You cannot delete a transfer which is not draft or cancelled.'))
        return super(journal_exchange, self).unlink()
