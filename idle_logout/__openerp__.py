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
{
    'name': 'Idle Logout',
    'version': '1.0',
    'category': 'Custom',
    'price': 10.00,
    'currency': 'EUR',
    'summary': 'Idle Logout',
    'description': """
Idle Logout    """,
    'author': 'Grover Menacho',
    'website': 'http://www.grovermenacho.com',
    'depends': ['web'],
    'data': ['res_users_view.xml',
             'views/idle_logout.xml'],
    'qweb': [],
    'installable': True,
    'active': False,
    'application': True,
}