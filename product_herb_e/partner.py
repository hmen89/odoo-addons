from openerp.osv import osv, fields
import openerp
from openerp import api
from openerp import SUPERUSER_ID, models


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'dob': fields.date('Date of Birth'),

        'reco_patient_id': fields.char('Patient ID', size=32),
        'reco_issued': fields.date('Issued'),
        'reco_expired': fields.date('Expired'),

        'reco_issuer': fields.char('Issuer Name', size=64),
        'reco_license': fields.char('Issuer License', size=32),
        'reco_verification_url': fields.char('Verification URL', size=128),
        'verified': fields.boolean('Verified')
    }

    _defaults = {
        'verified': True,
    }


res_partner()

class res_users(osv.osv):
    _inherit = 'res.users'

    def check_credentials(self, cr, uid, password):
        super(res_users, self).check_credentials(cr, uid, password)
        res2 = self.search(cr, SUPERUSER_ID, [('id', '=', uid), ('verified', '=', True)])
        if not res2:
            raise openerp.exceptions.AccessDenied()

res_users