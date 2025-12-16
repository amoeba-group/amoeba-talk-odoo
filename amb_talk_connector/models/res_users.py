import logging
import secrets
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    api_rest_key = fields.Char(string="API Rest Key", copy=False)
    api_domain = fields.Char(string="API Domain", copy=False)
    
    api_allow_partner = fields.Boolean(string="Allow Partner", default=True)
    api_allow_partner_create = fields.Boolean(string="Allow Partner Create", default=False)
    
    api_allow_countries = fields.Boolean(string="Allow Countries", default=True)
    
    api_allow_states = fields.Boolean(string="Allow States", default=True)
    
    api_allow_product = fields.Boolean(string="Allow Product", default=True)
    api_allow_product_template = fields.Boolean(string="Allow Product Template", default=True)
    
    api_allow_tax = fields.Boolean(string="Allow Tax", default=True)
    
    api_allow_sale_order = fields.Boolean(string="Allow Sale Order", default=True)
    api_allow_sale_order_create = fields.Boolean(string="Allow Sale Order Create", default=False)


    def generate_api_rest_key(self):
        self.ensure_one()
        if self.api_rest_key:
            return
        while True:
            api_rest_key = secrets.token_urlsafe(40)
            if not self.sudo().search([('api_rest_key', '=', api_rest_key)]):
                self.sudo().write({'api_rest_key': api_rest_key})
                return

    @api.model
    def get_api_rest_user(self, api_rest_key):
        return self.sudo().search([('api_rest_key', '=', api_rest_key)], limit=1)