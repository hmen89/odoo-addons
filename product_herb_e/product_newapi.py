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

from openerp import models, fields, api, _


class ProductProduct(models.Model):

    _inherit = 'product.product'

    @api.one
    @api.depends('uom_id')
    def _compute_inventory_type(self):
        if self.uom_id.name.lower() in ['g', 'gram'] and self.uom_id.category_id.name == 'Weight':
            self.inventory_type = 'weight'
        else:
            self.inventory_type = 'unit'

    inventory_type = fields.Selection([('weight','Weight'),('unit','Unit')],string='Inventory Type', compute=_compute_inventory_type, copy=False)

class PosCategory(models.Model):

    _inherit = 'pos.category'

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if context is None:
            context = {}
        if context.get('pos_ui'):
            categs_not_shown = []
            product_obj = self.pool.get('product.product')

            product_categ_ids = super(PosCategory, self).search(cr, uid, [('product_category','=',True)])

            products_not_for_sale = product_obj.search(cr, uid, [('sale_ok','=',False),('inventory_type','=','weight')])
            product_names = []
            for pr in product_obj.browse(cr, uid, products_not_for_sale):
                prod_name = pr.name.replace(' Gram', '')
                product_names.append(prod_name)

            print product_names

            for pc in self.browse(cr, uid, product_categ_ids):
                if pc.name in product_names:
                    categs_not_shown.append(pc.id)
            args.append((('id', 'not in', categs_not_shown)))
            print categs_not_shown
            print args
        return super(PosCategory, self).search(cr, uid, args, offset=offset, limit=limit, order=order,
                                                   context=context, count=count)