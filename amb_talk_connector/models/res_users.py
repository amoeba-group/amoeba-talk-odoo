import logging
import secrets
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)

class ResUsers(models.Model):
    _inherit = 'res.users'

    api_rest_key = fields.Char(string="API Rest Key", copy=False)
    api_domain = fields.Char(string="API Domain", copy=False)
    
    api_allow_partner = fields.Boolean(string="Partner", default=True)
    api_allow_partner_create = fields.Boolean(string="Partner Create", default=True)
    api_allow_partner_write = fields.Boolean(string="Partner Write", default=True)
    api_allow_partner_delete = fields.Boolean(string="Partner Delete", default=True)
    
    api_allow_countries = fields.Boolean(string="Countries", default=True)
    
    api_allow_states = fields.Boolean(string="States", default=True)
    
    api_allow_product = fields.Boolean(string="Product", default=True)
    api_allow_product_template = fields.Boolean(string="Product Template", default=True)
    
    api_allow_tax = fields.Boolean(string="Tax", default=True)
    
    api_allow_sale_order = fields.Boolean(string="Sale Order", default=True)
    api_allow_sale_order_create = fields.Boolean(string="Sale Order Create", default=True)
    api_allow_sale_order_write = fields.Boolean(string="Sale Order Write", default=True)
    # api_allow_sale_order_delete = fields.Boolean(string="Sale Order Delete", default=True)


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