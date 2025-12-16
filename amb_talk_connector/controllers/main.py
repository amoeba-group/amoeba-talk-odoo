from odoo import http
from odoo.http import request
from datetime import datetime
import json
import traceback
import logging

_logger = logging.getLogger(__name__)

class ApiAuthBaseController(http.Controller):
    """Base controller với transaction logging"""
    
    def _get_request_info(self):
        """Lấy thông tin từ request"""
        return {
            'ip': request.httprequest.remote_addr,
            'user_agent': request.httprequest.headers.get('User-Agent', ''),
            'origin': self._get_request_origin(),
            'params': dict(request.httprequest.args),
            'method': request.httprequest.method,
        }
    
    def _get_request_origin(self):
        """Lấy origin/domain từ request"""
        from urllib.parse import urlparse
        
        origin = request.httprequest.headers.get('Origin')
        if origin:
            parsed = urlparse(origin)
            return parsed.netloc or parsed.path
        
        referer = request.httprequest.headers.get('Referer')
        if referer:
            parsed = urlparse(referer)
            return parsed.netloc
        
        return request.httprequest.headers.get('Host', '')

    def _validate_domain(self, user, request_domain):
        """Kiểm tra domain có được phép không"""
        if not user.api_domain:
            return True
        
        allowed_domains = [d.strip().lower() for d in user.api_domain.split(',')]
        request_domain_lower = request_domain.lower()
        
        for allowed in allowed_domains:
            if allowed == '*':
                return True
            if allowed.startswith('*.'):
                base_domain = allowed[2:]
                if request_domain_lower.endswith(base_domain):
                    return True
            elif allowed == request_domain_lower:
                return True
        
        return False

    def _validate_token(self):
        """Kiểm tra Bearer token, domain và trả về user"""
        Authorization = request.httprequest.headers.get("Authorization")
        current_timestamp = datetime.utcnow().isoformat() + "Z"

        if not Authorization or not Authorization.startswith('Bearer '):
            return None, {
                'status': 'error',
                'message': 'Missing or invalid Authorization header (Bearer token required)',
                'timestamp': current_timestamp
            }, 401

        token = Authorization.replace('Bearer ', '')
        try:
            user = request.env['res.users'].sudo().get_api_rest_user(token)
            if not user:
                return None, {
                    'status': 'error',
                    'message': 'Authentication failed: Invalid token',
                    'timestamp': current_timestamp
                }, 401
            
            request_domain = self._get_request_origin()
            if not self._validate_domain(user, request_domain):
                return None, {
                    'status': 'error',
                    'message': f'Domain not allowed: {request_domain}',
                    'timestamp': current_timestamp,
                    'allowed_domains': user.api_domain or 'Not configured'
                }, 403
            
            return user, None, 200
            
        except Exception as e:
            return None, {
                'status': 'error',
                'message': f'Authentication error: {str(e)}',
                'timestamp': current_timestamp
            }, 500

    def _create_transaction_log(self, endpoint, version='v1', user=None, response_data=None, status='success', response_status=200, error_message=None, start_time=None):
        """Tạo log cho transaction"""
        try:
            request_info = self._get_request_info()
            
            # Lấy token (chỉ lưu 10 ký tự cuối)
            token = None
            auth_header = request.httprequest.headers.get("Authorization", "")
            if auth_header.startswith('Bearer '):
                full_token = auth_header.replace('Bearer ', '')
                token = f"...{full_token[-10:]}" if len(full_token) > 10 else full_token
            
            # Prepare request body
            request_body = None
            if request.httprequest.method in ['POST', 'PUT', 'PATCH']:
                try:
                    request_body = request.httprequest.get_data(as_text=True)
                except:
                    request_body = None
            
            log_data = {
                'endpoint': endpoint,
                'version': version,
                'method': request_info['method'],
                'user_id': user.id if user else None,
                'token': token,
                'request_origin': request_info['origin'],
                'request_ip': request_info['ip'],
                'request_user_agent': request_info['user_agent'],
                'request_params': json.dumps(request_info['params']) if request_info['params'] else None,
                'request_body': request_body,
                'response_status': response_status,
                'response_data': json.dumps(response_data, ensure_ascii=False) if response_data else None,
                'response_message': response_data.get('message') if isinstance(response_data, dict) else None,
                'status': status,
                'error_message': error_message,
                'start_time': start_time or datetime.utcnow(),
                'end_time': datetime.utcnow(),
            }
            
            request.env['api.transaction.log'].sudo().create(log_data)
            
        except Exception as e:
            _logger.error(f"Failed to create transaction log: {str(e)}")

    def _make_response(self, data, status=200):
        """Helper tạo response chuẩn"""
        return http.Response(
            json.dumps(data, ensure_ascii=False),
            content_type='application/json; charset=utf-8',
            status=status
        )


class ApiAuthV1Controller(ApiAuthBaseController):
    """API Authentication Version 1 with Transaction Logging"""
    
    @http.route('/api/v1/auth/check', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def check_connection_v1(self, **kwargs):
        """API kiểm tra kết nối - Version 1"""
        start_time = datetime.utcnow()
        user = None
        response_data = None
        status_code = 200
        log_status = 'success'
        error_msg = None
        
        try:
            user, error_response, status_code = self._validate_token()

            if error_response:
                response_data = error_response
                log_status = 'error'
                error_msg = error_response.get('message')
                self._create_transaction_log(
                    endpoint='/api/v1/auth/check',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)

            response_data = {
                'status': 'success',
                'message': 'Connection established successfully',
                'version': 'v1',
                'odoo_version': request.env['ir.config_parameter'].sudo().get_param('database.version', '18.0'),
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/auth/check',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
            
        except Exception as e:
            error_msg = str(e)
            response_data = {
                'status': 'error',
                'message': f'Internal server error: {error_msg}',
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/auth/check',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)

    @http.route('/api/v1/auth/user-info', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_user_info_v1(self, **kwargs):
        """Lấy thông tin user - Version 1"""
        start_time = datetime.utcnow()
        user = None
        response_data = None
        status_code = 200
        log_status = 'success'
        error_msg = None
        
        try:
            user, error_response, status_code = self._validate_token()

            if error_response:
                response_data = error_response
                log_status = 'error'
                error_msg = error_response.get('message')
                self._create_transaction_log(
                    endpoint='/api/v1/auth/user-info',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)

            response_data = {
                'status': 'success',
                'version': 'v1',
                'data': {
                    'id': user.id,
                    'name': user.name,
                    'login': user.login,
                    'email': user.email,
                    'company': [{
                        'id': company.id,
                        'name': company.name
                    }for company in user.company_ids] 
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/auth/user-info',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
            
        except Exception as e:
            error_msg = str(e)
            response_data = {
                'status': 'error',
                'message': error_msg
            }
            log_status = 'failed'
            status_code = 500
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/auth/user-info',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)