# -*- coding: utf-8 -*-

from openerp import SUPERUSER_ID
from openerp.addons.web import http
from openerp.addons.web.http import request
from openerp.addons.website_sale.controllers.main import website_sale
from openerp.addons.website.models.website import slug

class website_product_category(website_sale):
    def _get_search_domain(self, search, category, attrib_values):
        domain = request.website.sale_product_domain()
        if search:
            for srch in search.split(" "):
                domain += [
                    '|', '|', '|', ('name', 'ilike', srch), ('description', 'ilike', srch),
                    ('description_sale', 'ilike', srch), ('product_variant_ids.default_code', 'ilike', srch)]

        if category:
            domain += [('public_categ_ids', '=', int(category))]
        else:
            domain += [('public_categ_ids', '=', None)]

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

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>'
    ], type='http', auth="public", website=True)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        r = super(website_product_category, self).shop(page=page, category=category, search=search, ppg=ppg, **post)

        child_categ_ids = []

        if category:

            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)

            category_obj = pool['product.public.category']
            category_ids = category_obj.search(cr, uid, [('parent_id', '=', category.id),('on_screen','=',True)], context=context)
            categs = category_obj.browse(cr, uid, category_ids, context=context)

            for c in categs:
                child_categ_ids.append(c)

        else:
            category_obj = pool['product.public.category']
            category_ids = category_obj.search(cr, uid, [('parent_id', '=', None),('on_screen','=',True)], context=context)
            categs = category_obj.browse(cr, uid, category_ids, context=context)

            for c in categs:
                child_categ_ids.append(c)

        r.qcontext['child_categories'] = child_categ_ids



        return r