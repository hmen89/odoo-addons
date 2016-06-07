

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
import time

class pos_order(osv.osv):
    _inherit = 'pos.order'
    _columns = {
                    
                
    }
    
    def create_picking(self, cr, uid, ids, context=None):
        resp = super(pos_order, self).create_picking(cr, uid, ids, context=context)

        mfg_prod_id = []
        for order in self.browse(cr, uid, ids):
            for line in order.lines:
                if line.product_id.route_ids:
                    if 'Manufacture' in [l.name for l in line.product_id.route_ids]:
                        mfg_prod_id.append(line.product_id.id)

        # Auto Create MFG Order.
        if mfg_prod_id:
            time.sleep(2)
            proc_comp_pool = self.pool.get('procurement.orderpoint.compute')
            temp_id = proc_comp_pool.create(cr, uid, {})
            proc_comp_pool.procure_calculation(cr, uid, [temp_id])
        
        return resp

pos_order()

class procurement_order(osv.osv):
    _inherit = 'procurement.order'
    _columns = {
                
                
    }

    def make_mo(self, cr, uid, ids, context=None):
        resp = super(procurement_order, self).make_mo(cr, uid, ids, context=context)
        
        mfg_pool = self.pool.get('mrp.production')
        produce_pool = self.pool.get('mrp.product.produce')

        # Auto Assign and Auto Produce        
        for proc_id, mfg_id in resp.items():
            mfg = mfg_pool.browse(cr, SUPERUSER_ID, mfg_id)
            if mfg.state == 'confirmed':
                mfg_pool.action_assign(cr, SUPERUSER_ID, [mfg.id])
                mfg.refresh()
            
            if mfg.state == 'ready':
                ctx = {'active_id': mfg.id, 'active_ids':[mfg.id], 'active.model': 'mrp.production'}
                produce_id = produce_pool.create(cr, uid, {
                                                            'mode': 'consume_produce',
                                                            'product_qty' : mfg.product_qty, 
                                                            'consume_lines': [[0,0, {'product_id': m.product_id.id, 'product_qty': m.product_uom_qty}] for m in mfg.move_lines ] 
                                                        }, context=ctx)
                produce_pool.do_produce(cr, uid, [produce_id], context=ctx)
        return resp
    
procurement_order()
    

