

from openerp.osv import osv, fields

class product_new(osv.osv_memory):
    _name = 'product.new'
    _columns = {
                    
                    'inventory_type'   : fields.selection([('unit','Inventory by Unit'),('weight','Inventory by Weight')], 'Type'),
                    'name'             : fields.char('Product Name'),
                    'categ_id'         : fields.many2one('pos.category', 'PoS Category'),
                    'public_categ_id' : fields.many2one('product.public.category', 'Website Category'),
                    'description'    : fields.text('Description'),
                    
                    'image'          : fields.binary('Image'),
                
                    'unit_quantity' : fields.float('Quantity'),
                    'unit_cost' : fields.float('Cost per unit'),
                    'unit_price' : fields.float('Price per unit'),
                
                    'weight_quantity' : fields.float('Quantity (Grams)'),
                    'weight_cost' : fields.float('Cost per Gram'),
                    'weight_price' : fields.float('Price per Gram'),
                    
                    'sale_ok' : fields.boolean('Available for Sale'),
                    'publish' : fields.boolean('Publish to Website'),
                    'to_weight': fields.boolean('To Weight With Scale'),
                    
                    'line_ids' : fields.one2many('product.new.line', 'product_new_id', 'Lines'),

                    'mode': fields.char('Mode'),
                    'product_select_id': fields.many2one('product.product', 'Product'),
        'min_qty_18_oz': fields.boolean('Min. Qty 1/8 Oz.'),
    }
    _defaults = {
                    'sale_ok'  : True,
                    'publish'  : True,
                    'to_weight': True,
                    'line_ids' : [{'name':'1/8 Oz', 'weight':3.5}, {'name':'1/4 Oz', 'weight':7},{'name':'1/2 Oz', 'weight':14},{'name':'1 Oz', 'weight':28}],
                    
                    'inventory_type' : 'unit'
    }

    def get_next_barcode(self, cr, uid, context=None):
        sequence_pool = self.pool.get('ir.sequence')
        prod_pool = self.pool.get('product.product')
        while True:
            next_barcode = sequence_pool.next_by_code(cr, uid, 'product.barcode')
            barcode_exist = prod_pool.search(cr, uid, [('barcode','=',next_barcode)])
            if not barcode_exist:
                break
        return next_barcode

    def create_product(self, cr, uid, ids, context=None):
        sobj = self.browse(cr, uid, ids[0], context=context)
        
        pt_pool = self.pool.get('product.template')
        prod_pool = self.pool.get('product.product')
        qty_pool = self.pool.get('stock.change.product.qty')
        bom_pool = self.pool.get('mrp.bom')
        bom_pool_line = self.pool.get('mrp.bom.line')
        op_pool = self.pool.get('stock.warehouse.orderpoint')
        categ_pool = self.pool.get('pos.category')
        public_categ_pool = self.pool.get('product.public.category')


        prod_created = []

        if sobj.inventory_type == 'unit':
            product_vals = {
                                'name'             : sobj.name,
                                'available_in_pos' : True,
                                'pos_categ_id'     : sobj.categ_id.id,
                                'public_categ_ids' : [[6,0,[sobj.public_categ_id.id]]],
                                'description'      : sobj.description,
                                'list_price'       : sobj.unit_price,
                                'standard_price'   : sobj.unit_cost,
                                'type'             : 'product',
                                
                                'sale_ok'           : sobj.sale_ok,
                                'website_published' : sobj.publish,
                                
                                'image'            : sobj.image,
                                'herb_e'           : True,
            }

            if sobj.product_select_id:
                pt_id = sobj.product_select_id.product_tmpl_id.id
                prod_ids = prod_pool.search(cr, uid, [('product_tmpl_id','=',pt_id)])
            else:
                product_vals['barcode'] = self.get_next_barcode(cr, uid, context)
                pt_id = pt_pool.create(cr, uid, product_vals)
                prod_ids = prod_pool.search(cr, uid, [('product_tmpl_id','=',pt_id)])

            if prod_ids and sobj.unit_quantity>0:
                location_id = qty_pool.default_get(cr, uid, ['location_id'], context={'active_model':'product.product', 'active_id': prod_ids[0], 'active_ids' : prod_ids})
                qty_ids = qty_pool.create(cr, uid, {'product_id': prod_ids[0], 'new_quantity': sobj.unit_quantity})
                qty_pool.change_product_qty(cr, uid, qty_ids, context={})

            prod_created.append(pt_id)

        elif sobj.inventory_type == 'weight':

            old_categ_name = False
            if sobj.product_select_id:
                old_categ_name = sobj.product_select_id.pos_categ_id.name

            uom_pool = self.pool.get('product.uom')
            uom_ids = uom_pool.search(cr, uid, [('category_id.name','=','Weight'),'|',('name','=','g'),('name','ilike','gram')])
            if not uom_ids:
                raise osv.except_osv('UoM for Gram is not found', 'UoM for Gram is not found, please make sure there is UoM exist with name "g" or "gram" ')

            prod_categ_ids = categ_pool.search(cr, uid, [('name','=',sobj.name),('parent_id','=',sobj.categ_id.id)])
            if not prod_categ_ids:
                prod_categ_id = categ_pool.create(cr, uid, {'image':sobj.image, 'name': sobj.name, 'parent_id': sobj.categ_id.id, 'product_category':True, 'on_screen': sobj.sale_ok})
            else:
                prod_categ_id = prod_categ_ids[0]
                categ_pool.write(cr, uid, [prod_categ_id], {'image': sobj.image, 'on_screen': sobj.sale_ok})

            public_categ_ids = public_categ_pool.search(cr, uid, [('name','=',sobj.name),('parent_id','=',sobj.public_categ_id.id)])
            if not public_categ_ids:
                public_categ_id = public_categ_pool.create(cr, uid, {'image': sobj.image, 'name': sobj.name, 'parent_id': sobj.public_categ_id.id, 'product_category':True, 'on_screen': sobj.sale_ok})
            else:
                public_categ_id = public_categ_ids[0]
                public_categ_pool.write(cr, uid, [public_categ_id], {'image': sobj.image, 'on_screen': sobj.sale_ok})

            product_vals = {
                                'name'             : sobj.name + ' Gram',
                                'sort_code'        : sobj.name.lower().replace(' ','') + '_0',
                                'available_in_pos' : True,
                                'pos_categ_id'     : prod_categ_id,
                                'public_categ_ids' : [[6,0,[public_categ_id]]],
                                'description'      : sobj.description,
                                'type'             : 'product',
                                'list_price'       : sobj.weight_price,
                                'standard_price'   : sobj.weight_cost,
                                
                                'sale_ok'           : sobj.sale_ok,
                                'website_published' : sobj.publish,
                                'to_weight'         : sobj.to_weight,
                                'min_qty_18_oz'     : sobj.min_qty_18_oz,
                                
                                'image'             : sobj.image,
                                'uom_id'            : uom_ids[0],
                                'uom_po_id'         : uom_ids[0],

                                'barcode'          : self.get_next_barcode(cr, uid, context),
                                'herb_e'           : True,
            }

            if sobj.product_select_id:
                pt_id = sobj.product_select_id.product_tmpl_id.id
                pt_pool.write(cr, uid, [pt_id], product_vals)
                prod_ids = prod_pool.search(cr, uid, [('product_tmpl_id','=',pt_id)])
            else:
                pt_id = pt_pool.create(cr, uid, product_vals)
                prod_ids = prod_pool.search(cr, uid, [('product_tmpl_id','=',pt_id)])


            if prod_ids and sobj.weight_quantity>0:
                location_id = qty_pool.default_get(cr, uid, ['location_id'], context={'active_model':'product.product', 'active_id': prod_ids[0], 'active_ids' : prod_ids})
                qty_ids = qty_pool.create(cr, uid, {'product_id': prod_ids[0], 'new_quantity': sobj.weight_quantity})
                prod_pool.write(cr, uid, prod_ids, {'sort_code': product_vals['sort_code']})
                qty_pool.change_product_qty(cr, uid, qty_ids, context={})

            prod_created.append(pt_id)

            mfg_route_ids = self.pool.get('stock.location.route').search(cr, uid, [('product_selectable','=',True),('name','=','Manufacture')])
            if not mfg_route_ids:
                raise osv.except_osv('Manufacturing Route not Found', 'Manufacturing Route nout found')

            var_index = 1
            for variant in sobj.line_ids:

                if variant.price:
                    prod_var_vals = {
                                        'name'             : sobj.name + ' ' +  variant.name,
                                        'sort_code'        : sobj.name.lower().replace(' ','') + '_' + str(var_index),
                                        'available_in_pos' : True,
                                        'pos_categ_id'     : prod_categ_id,
                                        'public_categ_ids' : [[6,0,[public_categ_id]]],

                                        'description'      : sobj.description,
                                        'type'             : 'product',
                                        
                                        'sale_ok'           : sobj.sale_ok,
                                        'website_published' : sobj.publish ,
                                        'to_weight'         : sobj.to_weight,
                                        'image'             : sobj.image,

                                        'list_price'       : variant.price,
                                        'base_product_id'  : pt_id,
                                        
                                        'route_ids'        : [[6,0,[mfg_route_ids[0]]]],
                                        'barcode'          : self.get_next_barcode(cr, uid, context)
                    }

                    var_index += 1
                    if variant.product_select_id:
                        pt_var_id = variant.product_select_id.id
                        pt_pool.write(cr, uid, [pt_var_id], prod_var_vals)
                        prod_var_ids = prod_pool.search(cr, uid, [('product_tmpl_id','=',pt_var_id)])
                    else:
                        pt_var_id = pt_pool.create(cr, uid, prod_var_vals)
                        prod_var_ids = prod_pool.search(cr, uid, [('product_tmpl_id','=',pt_var_id)])

                    prod_pool.write(cr, uid, prod_var_ids, {'sort_code': prod_var_vals['sort_code']})
                    prod_created.append(pt_var_id)

                    if variant.product_select_id:
                        if variant.product_select_id.bom_ids:
                            bom_pool_line.write(cr, uid, [variant.product_select_id.bom_ids[0].bom_line_ids[0].id], {'product_qty': variant.weight})
                    else:
                        bom_pool.create(cr, uid, {
                                                'name' : sobj.name + ' ' +  variant.name,
                                                'product_tmpl_id' : pt_var_id,
                                                'product_id'      : prod_var_ids[0],
                                                'product_qty'     : 1,
                                                'type'            : 'normal',
                                                
                                                'bom_line_ids'    : [[0,0,{
                                                                            'product_id'  : prod_ids[0],
                                                                            'product_qty' : variant.weight,
                                                                            'product_uom' : uom_ids[0]
                                                                        }]]
                                              })
                    
                        op_vals = op_pool.default_get(cr, uid, ['name', 'warehouse_id', 'location_id', 'company_id'], context=context)
                        op_vals ['product_id'] = prod_var_ids[0]
                        op_vals ['product_min_qty'] = 0
                        op_vals ['product_max_qty'] = 0
                        op_vals ['qty_multiple'] = 1
                        op_pool.create(cr, uid, op_vals)

            if old_categ_name:
                for categ_id in categ_pool.search(cr, uid, [('name','=',old_categ_name)]):
                    pt_exist = pt_pool.search(cr, uid, [('pos_categ_id','=',categ_id)])
                    if not pt_exist:
                        categ_pool.unlink(cr, uid, [categ_id])

                for categ_id in public_categ_pool.search(cr, uid, [('name','=',old_categ_name)]):
                    pt_exist = pt_pool.search(cr, uid, [('public_categ_ids','in',categ_id)])
                    if not pt_exist:
                        public_categ_pool.unlink(cr, uid, [categ_id])


            if pt_id:
                if sobj.min_qty_18_oz:
                    pt_pool.write(cr, uid, [pt_id], {'sale_ok': False})

        if prod_created:
            return {
                'type'      : 'ir.actions.act_window',
                'name'      : sobj.name,
                'res_model' : 'product.template',
                'view_mode' : 'kanban,form,tree',
                'domain'    : [('id','in',prod_created)]
            }

    def onchange_categ_id(self, cr, uid, ids, categ_id, context=None):
        res = {'value':{}}
        if categ_id:
            categ = self.pool.get('pos.category').browse(cr, uid, categ_id)
            pub_categ_pool = self.pool.get('product.public.category')
            pub_categ_ids = pub_categ_pool.search(cr, uid, [('name','=',categ.name)])
            if len(pub_categ_ids) == 1:
                res = {'value':{'public_categ_id': pub_categ_ids[0]}}
            else:
                return {'warning': { 'title': 'Website Category', 'message': "There is no website category '%s', Please Create it first" %categ.name}}
        else:
            res = {'value':{'public_categ_id':False}}

        return res

    def onchage_product_selected(self, cr, uid, ids, product_select_id, context=None):
        ret = {'value':{}}
        if product_select_id:
            ret['value']['mode'] = 'update'
            prod = self.pool.get('product.product').browse(cr, uid, product_select_id)

            # Inventory By
            if prod.uom_id.name.lower() in ['g','gram'] and prod.uom_id.category_id.name == 'Weight':
                inventory_type = 'weight'
                ret['value']['inventory_type'] = 'weight'
            else:
                inventory_type = 'unit'
                ret['value']['inventory_type'] = 'unit'

            if prod.image:
                ret['value']['image'] = prod.image

            ret['value']['sale_ok']           = prod.sale_ok
            ret['value']['publish']           = prod.website_published
            ret['value']['to_weight']         = prod.to_weight
            ret['value']['description']       = prod.description
            ret['value']['min_qty_18_oz']     = prod.min_qty_18_oz

            if inventory_type == 'weight':
                prod_name = prod.name.replace(' Gram','')
                ret['value']['name'] = prod_name


                ret['value']['weight_quantity'] = prod.qty_available
                ret['value']['weight_cost'] = prod.standard_price
                ret['value']['weight_price'] = prod.list_price

                ret['value']['line_ids'] = [[6,0,[]]]
                for drv in prod.derivative_ids:
                    if drv.sale_ok:
                        ret['value']['sale_ok'] = drv.sale_ok
                    if drv.bom_ids:
                        for b_line in drv.bom_ids[0].bom_line_ids:
                            weight = b_line.product_qty

                    ret['value']['line_ids'].append({'name':drv.name.replace(prod_name, '').strip(), 'weight':weight, 'price':drv.list_price, 'product_select_id': drv.id})

                #PoS Category
                if prod.pos_categ_id.parent_id:
                    ret['value']['categ_id'] = prod.pos_categ_id.parent_id.id

                    #Website Category
                    if prod.public_categ_ids:
                        for cat in prod.public_categ_ids:
                            if cat.name == prod.pos_categ_id.name:
                                ret['value']['public_categ_id'] = cat.id


            elif inventory_type == 'unit':
                ret['value']['name'] = prod.name

                ret['value']['unit_quantity'] = prod.qty_available
                ret['value']['unit_cost'] = prod.standard_price
                ret['value']['unit_price'] = prod.list_price

                #PoS Category
                if prod.pos_categ_id:
                    ret['value']['categ_id'] = prod.pos_categ_id.id

                    #Website Category
                    if prod.public_categ_ids:
                        for cat in prod.public_categ_ids:
                            if cat.name == prod.pos_categ_id.name:
                                ret['value']['public_categ_id'] = cat.id



        return ret


product_new()

class product_new_line(osv.osv_memory):
    _name = 'product.new.line'
    _order = 'weight'
    _columns = {
                    'product_new_id' : fields.many2one('product.new'),
                
                    'name'   : fields.char('Unit Label'),
                    'weight' : fields.float('Weght (Grams)'),
                    'price'  : fields.float('Price'),

                    'product_select_id': fields.many2one('product.template', 'Product'),
    }
product_new_line()