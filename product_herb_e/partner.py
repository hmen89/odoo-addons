from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'dob': fields.date('Date of Birth'),

        'reco_patient_id': fields.char('Patient ID', size=32),
        'reco_issued': fields.date('Issued'),
        'reco_expired': fields.date('Expired'),

        'reco_issuer': fields.char('Issuer Name', size=64),
        'reco_license': fields.char('Issuer License', size=32),
        'reco_verification_URL': fields.char('Verification URL', size=128),

        'reco_verified': fields.char('Verified', size=64),
    }


res_partner()

