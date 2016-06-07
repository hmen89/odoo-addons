# -*- coding: utf-8 -*-
import base64

import werkzeug
import werkzeug.urls

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.tools.translate import _

from openerp.addons.website_form.controllers.main import WebsiteForm
from openerp.addons.website_sale.controllers.main import website_sale


class contact(http.Controller):

    @http.route(['/page/website.contacts', '/page/contacts'], type='http', auth="public", website=True)
    def contact(self, **kwargs):
        values = {}
        values['countries'] = request.env['res.country'].search([])
        return request.website.render("website.contacts", values)




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

