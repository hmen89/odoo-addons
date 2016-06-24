# -*- coding: utf-8 -*-
import openerp
from openerp import http
from openerp.http import request
import openerp.addons.website_sale.controllers.main

class website_sale(openerp.addons.website_sale.controllers.main.website_sale):

    @http.route(['/shop/order_placed'], type='http', auth="public", website=True)
    def manual_confirmation(self, **post):
        cr, uid, context = request.cr, request.uid, request.context

        order = request.website.sale_get_order(force_create=1, context=context)
        order_obj = request.registry['sale.order']

        contact_pool = request.registry['sale.contact.website']
        contact_ids = contact_pool.search(cr, uid, [])

        order.with_context(dict(context, send_email=True)).write({'state': 'sent'})

        if order:
            partners_contact = []
            for v in contact_pool.browse(cr, 1, contact_ids):
                partners_contact.append(v.user_id.partner_id.id)

            message = "New order: %s" % order.name or ''

            order.send_notification_to_contact('sale.order', partners_contact,
                                                message=message, context={})

        if not order:
            return request.redirect('/shop')

        #order.with_context(dict(context, send_email=True)).action_confirm()
        # clean context and session, then redirect to the confirmation page
        request.website.sale_reset(context=context)
        request.session.update({
            'website_sale_order': False,
        })
        return request.website.render("website_no_payment.order_confirmed", {'order': order})