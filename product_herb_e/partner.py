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


    def signup_herb(self, cr, uid, values, partner_values, token=None, context=None):
        """ signup a user, to either:
            - create a new user (no token), or
            - create a user for a partner (with token, but no user for partner), or
            - change the password of a user (with token, and existing user).
            :param values: a dictionary with field values that are written on user
            :param token: signup token (optional)
            :return: (dbname, login, password) for the signed up user
        """
        if token:
            # signup with a token: find the corresponding partner id
            res_partner = self.pool.get('res.partner')
            partner = res_partner._signup_retrieve_partner(
                cr, uid, token, check_validity=True, raise_exception=True, context=None)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False, 'verified': False})
            partner.write(partner_values)

            partner_user = partner.user_ids and partner.user_ids[0] or False

            # avoid overwriting existing (presumably correct) values with geolocation data
            if partner.country_id or partner.zip or partner.city:
                values.pop('city', None)
                values.pop('country_id', None)
            if partner.lang:
                values.pop('lang', None)

            if partner_user:
                # user exists, modify it according to values
                values.pop('login', None)
                values.pop('name', None)
                partner_user.write(values)
                return (cr.dbname, partner_user.login, values.get('password'))
            else:
                # user does not exist: sign up invited user
                values.update({
                    'name': partner.name,
                    'partner_id': partner.id,
                    'email': values.get('email') or values.get('login'),
                })
                if partner.company_id:
                    values['company_id'] = partner.company_id.id
                    values['company_ids'] = [(6, 0, [partner.company_id.id])]
                self._signup_create_user(cr, uid, values, context=context)
        else:
            # no token, sign up an external user
            values['email'] = values.get('email') or values.get('login')
            self._signup_create_user(cr, uid, values, context=context)
            res_partner = self.pool.get('res.partner')
            res_partner_ids = res_partner.search(cr, uid, [('email','=',values.get('email') or values.get('login'))])
            if res_partner_ids:
                partner_id = res_partner.browse(cr, uid, res_partner_ids[0])
                partner_id.write(
                    {'verified': False})
                partner_id.write(partner_values)



        return (cr.dbname, values.get('login'), values.get('password'))

res_users