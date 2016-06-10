from openerp.osv import osv, fields
import openerp
from openerp import api
from openerp import SUPERUSER_ID, models, _


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
        'verified': fields.selection([('v','Yes'),('nv','No')], string='Verified')
    }

    _defaults = {
        'verified': 'v',
    }


res_partner()

class res_users(osv.osv):
    _inherit = 'res.users'

    def check_credentials(self, cr, uid, password):
        super(res_users, self).check_credentials(cr, uid, password)
        res2 = self.search(cr, SUPERUSER_ID, [('id', '=', uid), ('verified', '=', 'v')])
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

        partner_created = False
        res_partner = self.pool.get('res.partner')

        if token:
            # signup with a token: find the corresponding partner id
            partner = res_partner._signup_retrieve_partner(
                cr, uid, token, check_validity=True, raise_exception=True, context=None)
            # invalidate signup token
            partner.write({'signup_token': False, 'signup_type': False, 'signup_expiration': False, 'verified': 'nv'})
            partner.write(partner_values)

            partner_created = partner.id

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
            res_partner_ids = res_partner.search(cr, uid, [('email','=',values.get('email') or values.get('login'))])
            if res_partner_ids:
                partner_id = res_partner.browse(cr, uid, res_partner_ids[0])
                partner_id.write(
                    {'verified': 'nv'})
                partner_id.write(partner_values)
                partner_created = res_partner_ids[0]


        verifiers_pool = self.pool.get('herb.verifiers')
        verifiers_ids = verifiers_pool.search(cr, uid, [])

        if partner_created:
            partner_new_obj = res_partner.browse(cr, uid, partner_created)
            partners_verifiers = []
            for v in verifiers_pool.browse(cr, uid, verifiers_ids):
                partners_verifiers.append(v.user_id.partner_id.id)

            message = "Please verify user with name %s" % partner_new_obj.name or ''

            self.send_notification_to_verifiers(cr, uid, [partner_created], 'res.partner', partners_verifiers, message=message, context={})

        return (cr.dbname, values.get('login'), values.get('password'))

    def send_notification_to_verifiers(self, cr, uid, ids, model, partner_ids, message="", context=None):
        mail_thread_pool = self.pool.get('mail.thread')
        for res_id in ids:
            post_values = {
                'subject': _('Request for Verification'),
                'body': message,
                'partner_ids': partner_ids,
                'notified_partner_ids': partner_ids,
                'attachments': [],
            }
            subtype = 'mail.mt_comment'

            ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'mail', 'mt_comment')
            subtype_id = ref and ref[1] or False

            message_id = mail_thread_pool.message_custom_post(cr, uid, [0], type='notification', subtype=subtype,
                                                              model=model, res_id=res_id, context=context,
                                                              **post_values)


res_users()