
from openerp.osv import osv, fields

class product_template(osv.osv):
    _inherit = 'product.template'
    _order = 'sort_code,name'
    _columns = {
                    'base_product_id' : fields.many2one('product.template', 'Base Product'),
                    'derivative_ids'  : fields.one2many('product.template', 'base_product_id', 'Derivatives'),

                    'sort_code': fields.char('Sort Code'),
                    'herb_e'   : fields.boolean('Herb E'),
                    'min_qty_18_oz': fields.boolean('Min. Qty 1/8 Oz.'),
    }
    _defaults = {
                    'sort_code':False
    }

    def edit_in_wizard(self, cr, uid, ids, context=None):
        if not context:
            context = {}

        context['default_mode'] = 'edit'

        sobj = self.browse(cr, uid, ids[0])
        if sobj.herb_e:
            context['default_product_select_id'] = sobj.id
        elif sobj.base_product_id:
            context['default_product_select_id'] = sobj.base_product_id.id


        return {
            'name': 'Edit Herb-e New Product',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.new',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
        }

product_template()

class product_product(osv.osv):
    _inherit = 'product.product'
    _order = 'default_code,sort_code,name_template'
    _columns = {
                    'sort_code': fields.related('product_tmpl_id','sort_code',type='char',string='Sort Code', store=True)
    }
product_product()

class pos_category(osv.osv):
    _inherit = 'pos.category'
    _columns = {
                    'product_category': fields.boolean('Product Category'),
        'on_screen': fields.boolean('On Screen')
    }

    _defaults = {
        'on_screen': True
    }
pos_category()

class product_public_category(osv.osv):
    _inherit = 'product.public.category'
    _columns = {
                    'product_category': fields.boolean('Product Category'),
        'on_screen': fields.boolean('On Screen')
    }

    _defaults = {
        'on_screen': True
    }
product_public_category()