# -*- coding: utf-8 -*-

{
    'name': 'Herb-e Product Manager',
    'version': '1.0',
    'author': 'ZedeSTechnologies',
    'category': 'General',
    'sequence': 27,
    'summary': '',
    'website': 'http://zedestech.com',
    'description': """
                        Herb-e Product Manager

                        * New Product Wizard

    """,
    'images': [],
    'depends': ['product', 'point_of_sale', 'mrp', 'website_sale','website_form','web', 'mail_extension'],
    'data': [
        'views/templates.xml',
        'sequence.xml',
        'wizard/new_product.xml',
        'product.xml',
        'partner.xml',
        'verify_view.xml',
        'views/product_herb_e.xml',
        'views/website_contact.xml',
        'security/ir.model.access.csv',

    ],
    'qweb': ['static/src/xml/pos.xml'],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
