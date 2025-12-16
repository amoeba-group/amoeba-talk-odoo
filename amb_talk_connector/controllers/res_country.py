from odoo import http
from odoo.http import request
from datetime import datetime
import json
import traceback
import logging
from odoo.addons.amb_talk_connector.controllers.main import ApiAuthBaseController

_logger = logging.getLogger(__name__)


class ApiLocationV1Controller(ApiAuthBaseController):
    """API Location (Country & State) Version 1"""
    
    def _build_country_domain(self, filters):
        """Xây dựng domain từ filters cho country"""
        domain = []
        
        # Search by name or code
        if filters.get('search'):
            search_term = filters['search']
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
            domain.append(('code', 'ilike', search_term))
        
        # Filter by code
        if filters.get('code'):
            domain.append(('code', '=', filters['code'].upper()))
        
        # Filter by phone_code
        if filters.get('phone_code'):
            domain.append(('phone_code', '=', filters['phone_code']))
        
        return domain
    
    def _build_state_domain(self, filters):
        """Xây dựng domain từ filters cho state"""
        domain = []
        
        # Search by name or code
        if filters.get('search'):
            search_term = filters['search']
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
            domain.append(('code', 'ilike', search_term))
        
        # Filter by country_id (required for most cases)
        if filters.get('country_id'):
            try:
                domain.append(('country_id', '=', int(filters['country_id'])))
            except ValueError:
                pass
        
        # Filter by country code
        if filters.get('country_code'):
            domain.append(('country_id.code', '=', filters['country_code'].upper()))
        
        # Filter by code
        if filters.get('code'):
            domain.append(('code', '=', filters['code'].upper()))
        
        return domain
    
    def _prepare_country_data(self, country, include_states=False):
        """Chuẩn bị data của country"""
        data = {
            'id': country.id,
            'name': country.name,
            'code': country.code,
            'phone_code': country.phone_code,
            'currency': {
                'id': country.currency_id.id,
                'name': country.currency_id.name,
                'symbol': country.currency_id.symbol,
            } if country.currency_id else None,
            'image_url': f'/web/image/res.country/{country.id}/image_512' if hasattr(country, 'image_512') else None,
        }
        
        # Include states if requested
        if include_states and hasattr(country, 'state_ids') and country.state_ids:
            data['states'] = []
            for state in country.state_ids:
                data['states'].append({
                    'id': state.id,
                    'name': state.name,
                    'code': state.code,
                })
        
        return data
    
    def _prepare_state_data(self, state):
        """Chuẩn bị data của state"""
        data = {
            'id': state.id,
            'name': state.name,
            'code': state.code,
            'country': {
                'id': state.country_id.id,
                'name': state.country_id.name,
                'code': state.country_id.code,
            } if state.country_id else None,
        }
        
        return data
    
    @http.route('/api/v1/countries', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_countries(self, **kwargs):
        """
        Lấy danh sách countries với phân trang, search, sort
        
        Query Parameters:
            - page: Số trang (default: 1)
            - page_size: Số records mỗi trang (default: 50, max: 250)
            - limit: Giới hạn số records (alternative to page_size)
            - offset: Bỏ qua số records (alternative to page)
            - sort: Trường sắp xếp (default: name)
            - order: Thứ tự sắp xếp: asc/desc (default: asc)
            - search: Tìm kiếm theo name hoặc code
            - code: Filter theo country code (VN, US, etc.)
            - phone_code: Filter theo phone code (84, 1, etc.)
            - include_states: Có include states không (true/false, default: false)
            
        Response:
            {
                "status": "success",
                "message": "Found X country(ies)",
                "version": "v1",
                "timestamp": "2024-11-25T10:00:00Z",
                "data": [...],
                "pagination": {...}
            }
        """
        start_time = datetime.utcnow()
        user = None
        response_data = None
        status_code = 200
        log_status = 'success'
        error_msg = None
        
        try:
            # Validate token and domain
            user, error_response, status_code = self._validate_token()
            if error_response:
                response_data = error_response
                log_status = 'error'
                error_msg = error_response.get('message')
                self._create_transaction_log(
                    endpoint='/api/v1/countries',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_countries:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/countries',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            # Pagination parameters
            page = int(kwargs.get('page', 1))
            page_size = int(kwargs.get('page_size', kwargs.get('limit', 50)))
            page_size = min(page_size, 250)  # Max 250 records per page
            offset = int(kwargs.get('offset', (page - 1) * page_size))
            
            # Sort parameters
            sort_field = kwargs.get('sort', 'name')
            sort_order = kwargs.get('order', 'asc').lower()
            
            # Validate sort order
            if sort_order not in ['asc', 'desc']:
                sort_order = 'asc'
            
            order_by = f"{sort_field} {sort_order}"
            
            # Build domain from filters
            domain = self._build_country_domain(kwargs)
            
            # Include states?
            include_states = kwargs.get('include_states', 'false').lower() == 'true'
            
            # Get countries
            Country = request.env['res.country'].sudo()
            total_count = Country.search_count(domain)
            countries = Country.search(domain, limit=page_size, offset=offset, order=order_by)
            
            # Prepare response data
            countries_data = []
            for country in countries:
                try:
                    country_data = self._prepare_country_data(country, include_states=include_states)
                    countries_data.append(country_data)
                except Exception as e:
                    _logger.warning(f"Error preparing data for country {country.id}: {str(e)}")
                    continue
            
            response_data = {
                'status': 'success',
                'message': f'Found {total_count} country(ies)',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': countries_data,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size if page_size > 0 else 0,
                    'offset': offset,
                    'has_next': offset + page_size < total_count,
                    'has_previous': offset > 0,
                },
                'filters_applied': {
                    'search': kwargs.get('search'),
                    'code': kwargs.get('code'),
                    'phone_code': kwargs.get('phone_code'),
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/countries',
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
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/countries: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/countries',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/countries/<int:country_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_country_detail(self, country_id, **kwargs):
        """
        Lấy thông tin chi tiết 1 country theo ID
        
        URL Parameters:
            - country_id: ID của country
            
        Query Parameters:
            - include_states: Có include states không (true/false, default: true)
            
        Response:
            {
                "status": "success",
                "message": "Country retrieved successfully",
                "version": "v1",
                "timestamp": "2024-11-25T10:00:00Z",
                "data": {
                    "id": 233,
                    "name": "Vietnam",
                    "code": "VN",
                    ...
                }
            }
        """
        start_time = datetime.utcnow()
        user = None
        response_data = None
        status_code = 200
        log_status = 'success'
        error_msg = None
        
        try:
            # Validate token and domain
            user, error_response, status_code = self._validate_token()
            if error_response:
                response_data = error_response
                log_status = 'error'
                error_msg = error_response.get('message')
                self._create_transaction_log(
                    endpoint=f'/api/v1/countries/{country_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_countries:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/countries/{country_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            # Include states by default for detail view
            include_states = kwargs.get('include_states', 'true').lower() == 'true'
            
            # Get country
            country = request.env['res.country'].sudo().browse(country_id)
            
            if not country.exists():
                response_data = {
                    'status': 'error',
                    'message': f'Country with ID {country_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/countries/{country_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Prepare response data
            country_data = self._prepare_country_data(country, include_states=include_states)
            
            response_data = {
                'status': 'success',
                'message': 'Country retrieved successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': country_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/countries/{country_id}',
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
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/countries/{country_id}: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/countries/{country_id}',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/states', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_states(self, **kwargs):
        """
        Lấy danh sách states với phân trang, search, sort
        
        Query Parameters:
            - page: Số trang (default: 1)
            - page_size: Số records mỗi trang (default: 50, max: 500)
            - limit: Giới hạn số records (alternative to page_size)
            - offset: Bỏ qua số records (alternative to page)
            - sort: Trường sắp xếp (default: name)
            - order: Thứ tự sắp xếp: asc/desc (default: asc)
            - search: Tìm kiếm theo name hoặc code
            - country_id: Filter theo country ID (strongly recommended)
            - country_code: Filter theo country code (VN, US, etc.)
            - code: Filter theo state code
            
        Response:
            {
                "status": "success",
                "message": "Found X state(s)",
                "version": "v1",
                "timestamp": "2024-11-25T10:00:00Z",
                "data": [...],
                "pagination": {...}
            }
        """
        start_time = datetime.utcnow()
        user = None
        response_data = None
        status_code = 200
        log_status = 'success'
        error_msg = None
        
        try:
            # Validate token and domain
            user, error_response, status_code = self._validate_token()
            if error_response:
                response_data = error_response
                log_status = 'error'
                error_msg = error_response.get('message')
                self._create_transaction_log(
                    endpoint='/api/v1/states',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_states:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/states',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Pagination parameters
            page = int(kwargs.get('page', 1))
            page_size = int(kwargs.get('page_size', kwargs.get('limit', 50)))
            page_size = min(page_size, 500)  # Max 500 records per page
            offset = int(kwargs.get('offset', (page - 1) * page_size))
            
            # Sort parameters
            sort_field = kwargs.get('sort', 'name')
            sort_order = kwargs.get('order', 'asc').lower()
            
            # Validate sort order
            if sort_order not in ['asc', 'desc']:
                sort_order = 'asc'
            
            order_by = f"{sort_field} {sort_order}"
            
            # Build domain from filters
            domain = self._build_state_domain(kwargs)
            
            # Get states
            State = request.env['res.country.state'].sudo()
            total_count = State.search_count(domain)
            states = State.search(domain, limit=page_size, offset=offset, order=order_by)
            
            # Prepare response data
            states_data = []
            for state in states:
                try:
                    state_data = self._prepare_state_data(state)
                    states_data.append(state_data)
                except Exception as e:
                    _logger.warning(f"Error preparing data for state {state.id}: {str(e)}")
                    continue
            
            response_data = {
                'status': 'success',
                'message': f'Found {total_count} state(s)',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': states_data,
                'pagination': {
                    'total': total_count,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total_count + page_size - 1) // page_size if page_size > 0 else 0,
                    'offset': offset,
                    'has_next': offset + page_size < total_count,
                    'has_previous': offset > 0,
                },
                'filters_applied': {
                    'search': kwargs.get('search'),
                    'country_id': kwargs.get('country_id'),
                    'country_code': kwargs.get('country_code'),
                    'code': kwargs.get('code'),
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/states',
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
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/states: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/states',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/states/<int:state_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_state_detail(self, state_id, **kwargs):
        """
        Lấy thông tin chi tiết 1 state theo ID
        
        URL Parameters:
            - state_id: ID của state
            
        Response:
            {
                "status": "success",
                "message": "State retrieved successfully",
                "version": "v1",
                "timestamp": "2024-11-25T10:00:00Z",
                "data": {
                    "id": 1,
                    "name": "California",
                    "code": "CA",
                    ...
                }
            }
        """
        start_time = datetime.utcnow()
        user = None
        response_data = None
        status_code = 200
        log_status = 'success'
        error_msg = None
        
        try:
            # Validate token and domain
            user, error_response, status_code = self._validate_token()
            if error_response:
                response_data = error_response
                log_status = 'error'
                error_msg = error_response.get('message')
                self._create_transaction_log(
                    endpoint=f'/api/v1/states/{state_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_states:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/states/{state_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            # Get state
            state = request.env['res.country.state'].sudo().browse(state_id)
            
            if not state.exists():
                response_data = {
                    'status': 'error',
                    'message': f'State with ID {state_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/states/{state_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Prepare response data
            state_data = self._prepare_state_data(state)
            
            response_data = {
                'status': 'success',
                'message': 'State retrieved successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': state_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/states/{state_id}',
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
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/states/{state_id}: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/states/{state_id}',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)