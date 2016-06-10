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

def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


class herb_verifiers(osv.osv):
    _name='herb.verifiers'
    _columns={
        'user_id': fields.many2one('res.users','User who verifies'),
    }
