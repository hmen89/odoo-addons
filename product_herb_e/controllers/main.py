# -*- coding: utf-8 -*-
import base64
import logging
import werkzeug
import werkzeug.urls

import openerp
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _


from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.website_form.controllers.main import WebsiteForm
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.auth_signup.controllers.main import AuthSignupHome

_logger = logging.getLogger(__name__)

class SignUp(AuthSignupHome):
    def _signup_with_values(self, token, values):
        db, login, password = request.registry['res.users'].signup(request.cr, openerp.SUPERUSER_ID, values, token)
        request.cr.commit()  # as authenticate will use its own cursor we need to commit the current transaction
        #uid = request.session.authenticate(db, login, password)
        #if not uid:
        #    raise SignupError(_('Authentication Failed.'))

    @http.route(['/web/signup','/page/website.getverified', '/page/getverified'], type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'reco_issuer' in qcontext and request.httprequest.method == 'POST':
            if qcontext.get('partner_id'):
                partner_id = int(qcontext.get('partner_id'))
                del qcontext['partner_id']
                try:
                    request.env['res.partner'].sudo().browse(partner_id).write(qcontext)
                    return self.contact_success(*args, **kw)
                except (SignupError, AssertionError), e:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not register your data. Try again.")


        if 'error' not in qcontext and 'reco_issuer' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                if qcontext.get('login'):
                    partner_ids = request.env["res.partner"].sudo().search([('email', '=', qcontext.get('login'))]).write({'verified': False})

                return self.contact(*args, **kw)
                #return super(AuthSignupHome, self).web_login(*args, **kw)
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        return request.render('auth_signup.signup', qcontext)

    def contact(self, *args, **kw):

        qcontext = request.params.copy()
        values = {}
        partner_id = False

        if kw.get('login'):
            partner_ids = request.env["res.partner"].sudo().search([('email', '=', qcontext.get('login'))])
            partner_id = partner_ids[0]

        values['countries'] = request.env['res.country'].search([])
        if qcontext and partner_id:
            values['name'] = qcontext.get('name')
            values['email_from'] = qcontext.get('login')
            values['partner_id'] = str(partner_id.id)
        return request.website.render("website.contacts", values)

    @http.route(['/page/website.contacts_thanks', '/page/contacts_thanks'], type='http', auth="public", website=True)
    def contact_success(self, *args, **kw):
        values = {}

        return request.website.render("website.contacts_thanks", values)





class WebsiteFormExt(WebsiteForm):

    WebsiteForm._input_filters['date'] = WebsiteForm.identity


class website_sale_ext(website_sale):

    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

        if category:
            domain += [('public_categ_ids', '=', int(category))]

        if attrib_values:
            attrib = None
            ids = []
            for value in attrib_values:
                if not attrib:
                    attrib = value[0]
                    ids.append(value[1])
                elif value[0] == attrib:
                    ids.append(value[1])
                else:
                    domain += [('attribute_line_ids.value_ids', 'in', ids)]
                    attrib = value[0]
                    ids = [value[1]]
            if attrib:
                domain += [('attribute_line_ids.value_ids', 'in', ids)]

        return domain

