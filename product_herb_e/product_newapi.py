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

class ProductProduct(models.Model):

    _name = 'product.product'
    _order = 'id desc'

    @api.one
    @api.depends('uom_id', 'uom_id.category_id')
    def _compute_inventory_type(self):
        if self.uom_id.name.lower() in ['g', 'gram'] and self.uom_id.category_id.name == 'Weight':
            self.inventory_type = 'weight'
        else:
            self.inventory_type = 'unit'

    inventory_type = fields.Selection([('weight','Weight'),('unit','Unit')],string='Inventory Type', compute=_compute_inventory_type, copy=False)