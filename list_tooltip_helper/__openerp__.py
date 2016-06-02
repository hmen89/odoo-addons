# -*- coding: utf-8 -*-
##############################################################################
#
#    Poiesis Consulting, OpenERP Partner
#    Copyright (C) 2013 Poiesis Consulting (<http://www.poiesisconsulting.com>).
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
    'name': 'List Tooltip Helper',
    'version': '1.0',
    'category': 'web',
    'price': 10.00,
    'currency': 'EUR',
    'sequence': 4,
    'summary': 'Allows you to check which column you are watching',
    'description': """
List Tooltip Helper
===================================
To be described soon
    """,
    'author': 'Grover Menacho',
    'website': 'http://www.grovermenacho.com',
    'depends': ['web'],
    'data': ['views/list_tooltip_helper.xml'],
    'installable': True,
    'active': False,
    'application': True,
    'qweb': [
        "static/src/xml/*.xml",
    ],
    'images': ['images/main_screenshot.png'],

#    'certificate': 'certificate',
}