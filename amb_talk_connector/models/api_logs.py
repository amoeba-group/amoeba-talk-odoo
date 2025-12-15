from odoo import fields, models, api
from datetime import datetime

class ApiTransactionLog(models.Model):
    _name = 'api.transaction.log'
    _description = 'API Transaction Log'
    _order = 'create_date desc'
    _rec_name = 'endpoint'

    # Thông tin cơ bản
    endpoint = fields.Char(string='Endpoint', required=True, index=True)
    version = fields.Char(string='API Version', default='v1', index=True)
    method = fields.Selection([
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
    ], string='HTTP Method', required=True, index=True)
    
    # User & Authentication
    user_id = fields.Many2one('res.users', string='User', ondelete='set null', index=True)
    token = fields.Char(string='Token (Last 10 chars)', help='Last 10 characters of token')
    
    # Request Information
    request_origin = fields.Char(string='Origin Domain', index=True)
    request_ip = fields.Char(string='IP Address', index=True)
    request_user_agent = fields.Text(string='User Agent')
    request_params = fields.Text(string='Request Parameters')
    request_body = fields.Text(string='Request Body')
    
    # Response Information
    response_status = fields.Integer(string='Response Status', index=True)
    response_data = fields.Text(string='Response Data')
    response_message = fields.Char(string='Response Message')
    
    start_time = fields.Datetime(string='Start Time', required=True)
    end_time = fields.Datetime(string='End Time')
    duration_ms = fields.Float(string='Duration (ms)', compute='_compute_duration', store=True)
    
    status = fields.Selection([
        ('success', 'Success'),
        ('error', 'Error'),
        ('failed', 'Failed'),
    ], string='Status', required=True, index=True, default='success')
    
    error_message = fields.Text(string='Error Message')
    error_type = fields.Char(string='Error Type')
    
    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration_ms = delta.total_seconds() * 1000
            else:
                record.duration_ms = 0.0
    
