# -*- coding: utf-8 -*-
import base64
import logging
import werkzeug
import werkzeug.urls

import openerp
from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.web.controllers.main import ensure_db


from openerp.addons.auth_signup.res_users import SignupError
from openerp.addons.website_form.controllers.main import WebsiteForm
from openerp.addons.website_sale.controllers.main import website_sale

_logger = logging.getLogger(__name__)


class HerbSignupHome(openerp.addons.web.controllers.main.Home):

    @http.route()
    def web_login(self, *args, **kw):
        ensure_db()
        response = super(HerbSignupHome, self).web_login(*args, **kw)
        response.qcontext.update(self.get_auth_signup_config())
        if request.httprequest.method == 'GET' and request.session.uid and request.params.get('redirect'):
            # Redirect if already logged in and redirect param is present
            return http.redirect_with_hash(request.params.get('redirect'))
        return response

    @http.route(['/website/page/getverified','/page/getverified'], type='http', auth='public', website=True)
    def web_auth_signup(self, *args, **kw):
        qcontext = self.get_auth_signup_qcontext()

        if not qcontext.get('token') and not qcontext.get('signup_enabled'):
            raise werkzeug.exceptions.NotFound()

        if 'error' not in qcontext and request.httprequest.method == 'POST':
            try:
                self.do_signup(qcontext)
                return self.contact_success(*args, **kw)
            except (SignupError, AssertionError), e:
                if request.env["res.users"].sudo().search([("login", "=", qcontext.get("login"))]):
                    qcontext["error"] = _("Another user is already registered using this email address.")
                else:
                    _logger.error(e.message)
                    qcontext['error'] = _("Could not create a new account.")

        return request.render('website.contacts', qcontext)

    def get_auth_signup_config(self):
        """retrieve the module config (which features are enabled) for the login page"""

        icp = request.registry.get('ir.config_parameter')
        return {
            'signup_enabled': icp.get_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.allow_uninvited') == 'True',
            'reset_password_enabled': icp.get_param(request.cr, openerp.SUPERUSER_ID, 'auth_signup.reset_password') == 'True',
        }

    def get_auth_signup_qcontext(self):
        """ Shared helper returning the rendering context for signup and reset password """
        qcontext = request.params.copy()
        qcontext.update(self.get_auth_signup_config())
        if qcontext.get('token'):
            try:
                # retrieve the user info (name, login or email) corresponding to a signup token
                res_partner = request.registry.get('res.partner')
                token_infos = res_partner.signup_retrieve_info(request.cr, openerp.SUPERUSER_ID, qcontext.get('token'))
                for k, v in token_infos.items():
                    qcontext.setdefault(k, v)
            except:
                qcontext['error'] = _("Invalid signup token")
                qcontext['invalid_token'] = True
        return qcontext

    def do_signup(self, qcontext):
        """ Shared helper that creates a res.partner out of a token """
        values = dict((key, qcontext.get(key)) for key in ('login', 'name', 'password'))
        partner_values = dict((key, qcontext.get(key)) for key in ('street', 'street2', 'city', 'zip', 'dob', 'phone', 'mobile', 'reco_patient_id', 'reco_issued', 'reco_expired', 'reco_issuer', 'reco_license', 'reco_verification_url'))
        assert any([k for k in values.values()]), "The form was not properly filled in."
        assert values.get('password') == qcontext.get('confirm_password'), "Passwords do not match; please retype them."
        supported_langs = [lang['code'] for lang in request.registry['res.lang'].search_read(request.cr, openerp.SUPERUSER_ID, [], ['code'])]
        if request.lang in supported_langs:
            values['lang'] = request.lang
        self._signup_with_values(qcontext.get('token'), values, partner_values)
        request.cr.commit()

    def _signup_with_values(self, token, values, partner_values):
        db, login, password = request.registry['res.users'].signup_herb(request.cr, openerp.SUPERUSER_ID, values, partner_values, token)
        request.cr.commit()     # as authenticate will use its own cursor we need to commit the current transaction
        #uid = request.session.authenticate(db, login, password)
        #if not uid:
        #    raise SignupError(_('Authentication Failed.'))


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

