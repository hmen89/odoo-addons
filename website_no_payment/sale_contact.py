# -*- coding: utf-8 -*-
##############################################################################
#    
#    Grover Menacho
#    Copyright (C) 2013 Grover Menacho (<http://www.grovermenacho.com>).
#    Coded by: Grover Menacho
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


from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import SUPERUSER_ID

from openerp import netsvc



class sale_contact_website(osv.osv):
    _name='sale.contact.website'
    _columns={
        'user_id': fields.many2one('res.users','User who verifies'),
    }


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def send_notification_to_contact(self, cr, uid, ids, model, partner_ids, message="", context=None):
        mail_thread_pool = self.pool.get('mail.thread')
        for res_id in ids:
            post_values = {
                'subject': _('A new sale order has been created'),
                'body': message,
                'partner_ids': partner_ids,
                'notified_partner_ids': partner_ids,
                'attachments': [],
            }
            subtype = 'mail.mt_comment'

            ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mail', 'mt_comment')
            subtype_id = ref and ref[1] or False

            message_id = mail_thread_pool.message_custom_post(cr, uid, [0], type='notification', subtype=subtype,
                                                              model=model, res_id=res_id, context=context,
                                                              **post_values)