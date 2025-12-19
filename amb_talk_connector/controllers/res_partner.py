# controllers/api_partner_v1.py
from odoo import http
from odoo.http import request
from datetime import datetime
import json
import traceback
import logging
from odoo.addons.amb_talk_connector.controllers.main import ApiAuthBaseController

_logger = logging.getLogger(__name__)


class ApiPartnerV1Controller(ApiAuthBaseController):
    """API Partner Version 1"""
# ====================== 1. PARTNER INFOR ==================================
    def _build_partner_domain(self, filters):
        """Xây dựng domain từ filters cho partner"""
        domain = [('id', '!=', [1,2,3,4,5,6])]
        
        # Search by name, email, phone, vat
        if filters.get('search'):
            search_term = filters['search']
            domain.append('|')
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
            domain.append(('email', 'ilike', search_term))
            domain.append(('phone', 'ilike', search_term))
            domain.append(('vat', 'ilike', search_term))
        
        # Filter by partner type (contact, invoice, delivery, etc.)
        if filters.get('type'):
            domain.append(('type', '=', filters['type']))
        
        # Filter by is_company
        if filters.get('is_company'):
            is_company = filters['is_company'].lower() in ['true', '1', 'yes']
            domain.append(('is_company', '=', is_company))
        
        # Filter by customer
        if filters.get('customer'):
            customer = filters['customer'].lower() in ['true', '1', 'yes']
            domain.append(('customer_rank', '>', 0) if customer else ('customer_rank', '=', 0))
        
        # Filter by supplier
        if filters.get('supplier'):
            supplier = filters['supplier'].lower() in ['true', '1', 'yes']
            domain.append(('supplier_rank', '>', 0) if supplier else ('supplier_rank', '=', 0))
        
        # Filter by active status
        if filters.get('active'):
            active = filters['active'].lower() in ['true', '1', 'yes']
            domain.append(('active', '=', active))
        else:
            # Default: only active partners
            domain.append(('active', '=', True))
        
        # Filter by parent_id (get only main contacts or child contacts)
        if filters.get('parent_id'):
            try:
                domain.append(('parent_id', '=', int(filters['parent_id'])))
            except ValueError:
                pass
        
        if filters.get('has_parent'):
            has_parent = filters['has_parent'].lower() in ['true', '1', 'yes']
            if has_parent:
                domain.append(('parent_id', '!=', False))
            else:
                domain.append(('parent_id', '=', False))
        
        # Filter by country
        if filters.get('country_id'):
            try:
                domain.append(('country_id', '=', int(filters['country_id'])))
            except ValueError:
                pass
        
        if filters.get('country_code'):
            domain.append(('country_id.code', '=', filters['country_code'].upper()))
        
        # Filter by state/province
        if filters.get('state_id'):
            try:
                domain.append(('state_id', '=', int(filters['state_id'])))
            except ValueError:
                pass
        
        # Filter by city
        if filters.get('city'):
            domain.append(('city', 'ilike', filters['city']))
        
        # Filter by company
        if filters.get('company_id'):
            try:
                domain.append(('company_id', '=', int(filters['company_id'])))
            except ValueError:
                pass
        
        # Filter by category
        if filters.get('category_id'):
            try:
                domain.append(('category_id', 'in', [int(filters['category_id'])]))
            except ValueError:
                pass
        
        return domain
    
    def _prepare_partner_data(self, partner, include_contacts=False, include_addresses=False):
        """Chuẩn bị data của partner"""
        data = {
            'id': partner.id,
            'name': partner.name,
            'display_name': partner.display_name,
            'ref': partner.ref,
            'type': partner.type,
            'is_company': partner.is_company,
            'is_customer': partner.customer_rank > 0,
            'is_supplier': partner.supplier_rank > 0,
            'active': partner.active,
            'email': partner.email,
            'phone': partner.phone,
            'mobile': partner.mobile,
            'website': partner.website,
            'vat': partner.vat,
            'street': partner.street,
            'street2': partner.street2,
            'city': partner.city,
            'zip': partner.zip,
            'state': {
                'id': partner.state_id.id,
                'name': partner.state_id.name,
                'code': partner.state_id.code,
            } if partner.state_id else None,
            'country': {
                'id': partner.country_id.id,
                'name': partner.country_id.name,
                'code': partner.country_id.code,
            } if partner.country_id else None,
            'parent': {
                'id': partner.parent_id.id,
                'name': partner.parent_id.name,
            } if partner.parent_id else None,
            'company': {
                'id': partner.company_id.id,
                'name': partner.company_id.name,
            } if partner.company_id else None,
            'user': {
                'id': partner.user_id.id,
                'name': partner.user_id.name,
            } if partner.user_id else None,
            'comment': partner.comment,
            'categories': [{'id': cat.id, 'name': cat.name} for cat in partner.category_id] if partner.category_id else [],
            'lang': partner.lang,
            'tz': partner.tz,
            'create_date': partner.create_date.isoformat() if partner.create_date else None,
            'write_date': partner.write_date.isoformat() if partner.write_date else None,
        }
        
        # Include child contacts
        if include_contacts and partner.child_ids:
            data['contacts'] = []
            for child in partner.child_ids:
                data['contacts'].append({
                    'id': child.id,
                    'name': child.name,
                    'type': child.type,
                    'email': child.email,
                    'phone': child.phone,
                    'mobile': child.mobile,
                    'function': child.function,
                })
        
        # Include all addresses (invoice, delivery, etc.)
        if include_addresses:
            data['addresses'] = {
                'invoice': None,
                'delivery': None,
                'contact': None,
                'other': None,
            }
            
            # Get address by type
            for child in partner.child_ids:
                address_info = {
                    'id': child.id,
                    'name': child.name,
                    'street': child.street,
                    'street2': child.street2,
                    'city': child.city,
                    'zip': child.zip,
                    'state': {
                        'id': child.state_id.id,
                        'name': child.state_id.name,
                    } if child.state_id else None,
                    'country': {
                        'id': child.country_id.id,
                        'name': child.country_id.name,
                        'code': child.country_id.code,
                    } if child.country_id else None,
                    'phone': child.phone,
                    'email': child.email,
                }
                
                if child.type == 'invoice':
                    data['addresses']['invoice'] = address_info
                elif child.type == 'delivery':
                    data['addresses']['delivery'] = address_info
                elif child.type == 'contact':
                    data['addresses']['contact'] = address_info
                elif child.type == 'other':
                    data['addresses']['other'] = address_info
        
        # Include payment term if available
        if hasattr(partner, 'property_payment_term_id') and partner.property_payment_term_id:
            data['payment_term'] = {
                'id': partner.property_payment_term_id.id,
                'name': partner.property_payment_term_id.name,
            }
        
        # Include supplier payment term if available
        if hasattr(partner, 'property_supplier_payment_term_id') and partner.property_supplier_payment_term_id:
            data['supplier_payment_term'] = {
                'id': partner.property_supplier_payment_term_id.id,
                'name': partner.property_supplier_payment_term_id.name,
            }
        
        return data
    
    @http.route('/api/v1/partners', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_partners(self, **kwargs):
        """
        Lấy danh sách partners với phân trang, search, sort
        
        Query Parameters:
            - page: Số trang (default: 1)
            - page_size: Số records mỗi trang (default: 20, max: 100)
            - limit: Giới hạn số records (alternative to page_size)
            - offset: Bỏ qua số records (alternative to page)
            - sort: Trường sắp xếp (default: name)
            - order: Thứ tự sắp xếp: asc/desc (default: asc)
            - search: Tìm kiếm theo name, email, phone, vat
            - type: Filter theo type (contact, invoice, delivery, other, private)
            - is_company: Filter theo company (true/false)
            - customer: Filter customers (true/false)
            - supplier: Filter suppliers (true/false)
            - active: Filter theo active status (true/false, default: true)
            - parent_id: Filter theo parent ID
            - has_parent: Filter partners có parent hay không (true/false)
            - country_id: Filter theo country ID
            - country_code: Filter theo country code (VN, US, etc.)
            - state_id: Filter theo state/province ID
            - city: Filter theo city
            - company_id: Filter theo company
            - category_id: Filter theo category ID
            - include_contacts: Có include child contacts không (true/false, default: false)
            - include_addresses: Có include addresses không (true/false, default: false)
            
        Response:
            {
                "status": "success",
                "message": "Found X partner(s)",
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
                    endpoint='/api/v1/partners',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_partner:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                # Log failed transaction
                self._create_transaction_log(
                    endpoint='/api/v1/partners',
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
            page_size = int(kwargs.get('page_size', kwargs.get('limit', 20)))
            page_size = min(page_size, 100)  # Max 100 records per page
            offset = int(kwargs.get('offset', (page - 1) * page_size))
            
            # Sort parameters
            sort_field = kwargs.get('sort', 'name')
            sort_order = kwargs.get('order', 'asc').lower()
            
            # Validate sort order
            if sort_order not in ['asc', 'desc']:
                sort_order = 'asc'
            
            order_by = f"{sort_field} {sort_order}"
            
            # Build domain from filters
            domain = self._build_partner_domain(kwargs)
            
            # Include options
            include_contacts = kwargs.get('include_contacts', 'false').lower() == 'true'
            include_addresses = kwargs.get('include_addresses', 'false').lower() == 'true'
            
            # Get partners
            Partner = request.env['res.partner'].sudo()
            total_count = Partner.search_count(domain)
            partners = Partner.search(domain, limit=page_size, offset=offset, order=order_by)
            
            # Prepare response data
            partners_data = []
            for partner in partners:
                try:
                    partner_data = self._prepare_partner_data(
                        partner,
                        include_contacts=include_contacts,
                        include_addresses=include_addresses
                    )
                    partners_data.append(partner_data)
                except Exception as e:
                    _logger.warning(f"Error preparing data for partner {partner.id}: {str(e)}")
                    continue
            
            response_data = {
                'status': 'success',
                'message': f'Found {total_count} partner(s)',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': partners_data,
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
                    'type': kwargs.get('type'),
                    'is_company': kwargs.get('is_company'),
                    'customer': kwargs.get('customer'),
                    'supplier': kwargs.get('supplier'),
                    'active': kwargs.get('active', 'true'),
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/partners',
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
            
            _logger.error(f"API Error at /api/v1/partners: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/partners',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/partners/<int:partner_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_partner_detail(self, partner_id, **kwargs):
        """
        Lấy thông tin chi tiết 1 partner theo ID
        
        URL Parameters:
            - partner_id: ID của partner
            
        Query Parameters:
            - include_contacts: Có include child contacts không (true/false, default: true)
            - include_addresses: Có include addresses không (true/false, default: true)
            
        Response:
            {
                "status": "success",
                "message": "Partner retrieved successfully",
                "version": "v1",
                "timestamp": "2024-11-25T10:00:00Z",
                "data": {
                    "id": 7,
                    "name": "Azure Interior",
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
                    endpoint=f'/api/v1/partners/{partner_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_partner:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                # Log failed transaction
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Include options - default to true for detail view
            include_contacts = kwargs.get('include_contacts', 'true').lower() == 'true'
            include_addresses = kwargs.get('include_addresses', 'true').lower() == 'true'
            
            # Get partner
            partner = request.env['res.partner'].sudo().browse(partner_id)
            
            if not partner.exists() or partner.id in [1,2,3,4,5,6]:
                response_data = {
                    'status': 'error',
                    'message': f'Partner with ID {partner_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}',
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
            partner_data = self._prepare_partner_data(
                partner,
                include_contacts=include_contacts,
                include_addresses=include_addresses
            )
            
            response_data = {
                'status': 'success',
                'message': 'Partner retrieved successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': partner_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/partners/{partner_id}',
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
            
            _logger.error(f"API Error at /api/v1/partners/{partner_id}: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/partners/{partner_id}',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
        
        
        
# ====================== 2. CREATE PARTNER ==================================
    def _validate_partner_data(self, data):
        """Validate dữ liệu partner trước khi tạo"""
        errors = []
        
        # Validate name (required)
        if not data.get('name'):
            errors.append("name is required")
        elif len(data['name'].strip()) < 2:
            errors.append("name must be at least 2 characters")
        
        # Validate email format if provided
        if data.get('email'):
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("email format is invalid")
        
        # Validate type if provided
        if data.get('type'):
            valid_types = ['contact', 'invoice', 'delivery', 'other', 'private']
            if data['type'] not in valid_types:
                errors.append(f"type must be one of: {', '.join(valid_types)}")
        
        # Validate country_id if provided
        if data.get('country_id'):
            try:
                country_id = int(data['country_id'])
                country = request.env['res.country'].sudo().browse(country_id)
                if not country.exists():
                    errors.append(f"Country with ID {country_id} not found")
            except (ValueError, TypeError):
                errors.append("country_id must be a valid integer")
        
        # Validate state_id if provided
        if data.get('state_id'):
            try:
                state_id = int(data['state_id'])
                state = request.env['res.country.state'].sudo().browse(state_id)
                if not state.exists():
                    errors.append(f"State with ID {state_id} not found")
            except (ValueError, TypeError):
                errors.append("state_id must be a valid integer")
        
        # Validate parent_id if provided
        if data.get('parent_id'):
            try:
                parent_id = int(data['parent_id'])
                parent = request.env['res.partner'].sudo().browse(parent_id)
                if not parent.exists():
                    errors.append(f"Parent partner with ID {parent_id} not found")
                # If has parent, should not be a company
                if data.get('is_company', False):
                    errors.append("A contact with parent_id cannot be a company")
            except (ValueError, TypeError):
                errors.append("parent_id must be a valid integer")
        
        # Validate user_id if provided
        if data.get('user_id'):
            try:
                user_id = int(data['user_id'])
                user = request.env['res.users'].sudo().browse(user_id)
                if not user.exists():
                    errors.append(f"User with ID {user_id} not found")
            except (ValueError, TypeError):
                errors.append("user_id must be a valid integer")
        
        # Validate company_id if provided
        if data.get('company_id'):
            try:
                company_id = int(data['company_id'])
                company = request.env['res.company'].sudo().browse(company_id)
                if not company.exists():
                    errors.append(f"Company with ID {company_id} not found")
            except (ValueError, TypeError):
                errors.append("company_id must be a valid integer")
        
        # Validate category_ids if provided
        if data.get('category_ids'):
            if not isinstance(data['category_ids'], list):
                errors.append("category_ids must be an array of integers")
            else:
                for cat_id in data['category_ids']:
                    try:
                        category = request.env['res.partner.category'].sudo().browse(int(cat_id))
                        if not category.exists():
                            errors.append(f"Category with ID {cat_id} not found")
                    except (ValueError, TypeError):
                        errors.append(f"Invalid category_id: {cat_id}")
        
        return errors
    
    @http.route('/api/v1/partners/create', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_partner(self, **kwargs):
        # f"""
        #     Tạo mới partner (contact/customer/supplier)
            
        #     Body (JSON):
        #         {
        #             "name": "Company Name",
        #             "ref": "REF001",
        #             "email": "contact@example.com",
        #             "phone": "+84 123 456 789",
        #             "mobile": "+84 987 654 321",
        #             "website": "https://example.com",
        #             "vat": "1234567890",
        #             "type": "contact",// Optional: Type (contact, invoice, delivery, other, private)
        #             "street": "123 Main Street",
        #             "street2": "Apt 4B",
        #             "city": "Ho Chi Minh City",
        #             "zip": "700000",
        #             "state_id": 1,
        #             "country_id": 233 
        #         }

        # """
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
                    endpoint='/api/v1/partners/create',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            # Get JSON data from request body
            try:
                raw = request.httprequest.data
                data = json.loads(raw.decode('utf-8'))
            except json.JSONDecodeError as e:
                response_data = {
                    'status': 'error',
                    'message': f'Invalid JSON format: {str(e)}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 400
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint='/api/v1/partners/create',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_partner_create:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/partners/create',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Validate input data
            validation_errors = self._validate_partner_data(data)
            if validation_errors:
                response_data = {
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': validation_errors,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 400
                log_status = 'error'
                error_msg = ', '.join(validation_errors)
                
                self._create_transaction_log(
                    endpoint='/api/v1/partners/create',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Prepare partner data
            partner_vals = {
                'name': data['name'].strip(),
            }
            
            # Optional fields
            if data.get('ref'):
                partner_vals['ref'] = data['ref']
            
            if data.get('email'):
                partner_vals['email'] = data['email']
            
            if data.get('phone'):
                partner_vals['phone'] = data['phone']
            
            if data.get('mobile'):
                partner_vals['mobile'] = data['mobile']
                
            if data.get('vat'):
                partner_vals['vat'] = data['vat']
            
            if data.get('is_company') is not None:
                partner_vals['is_company'] = data['is_company']
            else:
                # Default to True if not specified
                partner_vals['is_company'] = False
            
            if data.get('type'):
                partner_vals['type'] = data['type']
            
            if data.get('parent_id'):
                partner_vals['parent_id'] = int(data['parent_id'])
            
            if data.get('street'):
                partner_vals['street'] = data['street']
            
            if data.get('street2'):
                partner_vals['street2'] = data['street2']
            
            if data.get('city'):
                partner_vals['city'] = data['city']
            
            if data.get('zip'):
                partner_vals['zip'] = data['zip']
            
            if data.get('state_id'):
                partner_vals['state_id'] = int(data['state_id'])
            
            if data.get('country_id'):
                partner_vals['country_id'] = int(data['country_id'])
            
            if data.get('user_id'):
                partner_vals['user_id'] = user.id
            
            partner_vals['company_id'] = user.company_id.id
            
            
            # Handle category_ids
            if data.get('category_ids'):
                partner_vals['category_id'] = [(6, 0, [int(cat_id) for cat_id in data['category_ids']])]
            
            # Create partner
            Partner = request.env['res.partner'].sudo()
            partner = Partner.create(partner_vals)
            
            # Set as customer if requested
            if data.get('customer', False):
                partner.write({'customer_rank': 1})
            
            # Set as supplier if requested
            if data.get('supplier', False):
                partner.write({'supplier_rank': 1})
            
            # Prepare response
            partner_data = self._prepare_partner_data(partner, include_contacts=False, include_addresses=False)
            
            response_data = {
                'status': 'success',
                'message': 'Partner created successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': partner_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/partners/create',
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
                'message': f'Failed to create partner: {error_msg}',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/partners/create: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/partners/create',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
        
        
# ====================== 3. UPDATE PARTNER ==================================
    def _validate_partner_update_data(self, data):
        """Validate dữ liệu partner trước khi update - chỉ các field được phép"""
        errors = []
        
        # Validate name if provided
        if 'name' in data:
            if not data['name']:
                errors.append("name cannot be empty")
            elif len(data['name'].strip()) < 2:
                errors.append("name must be at least 2 characters")
        
        # Validate email format if provided
        if 'email' in data and data['email']:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data['email']):
                errors.append("email format is invalid")
        
        # Validate country_id if provided
        if 'country_id' in data and data['country_id']:
            try:
                country_id = int(data['country_id'])
                country = request.env['res.country'].sudo().browse(country_id)
                if not country.exists():
                    errors.append(f"Country with ID {country_id} not found")
            except (ValueError, TypeError):
                errors.append("country_id must be a valid integer")
        
        # Validate state_id if provided
        if 'state_id' in data and data['state_id']:
            try:
                state_id = int(data['state_id'])
                state = request.env['res.country.state'].sudo().browse(state_id)
                if not state.exists():
                    errors.append(f"State with ID {state_id} not found")
            except (ValueError, TypeError):
                errors.append("state_id must be a valid integer")
        
        # Check for non-allowed fields
        allowed_fields = [
            'name', 'email', 'phone', 'mobile', 'website', 'vat',
            'street', 'street2', 'city', 'zip', 'state_id', 'country_id',
            'lang', 'tz'
        ]
        
        non_allowed = [field for field in data.keys() if field not in allowed_fields]
        if non_allowed:
            errors.append(f"Fields not allowed for update: {', '.join(non_allowed)}")
        
        return errors
    
    @http.route('/api/v1/partners/<int:partner_id>/update', type='http', auth='public', methods=['PUT', 'PATCH'], csrf=False, cors='*')
    def update_partner(self, partner_id, **kwargs):
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
                    endpoint=f'/api/v1/partners/{partner_id}/update',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            # Check permission for update
            if not user.api_allow_partner_update:
                error_msg = "Access denied: You do not have permission to update partners."
                response_data = {
                    'status': 'error',
                    'message': error_msg,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/update',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Get partner
            partner = request.env['res.partner'].sudo().browse(partner_id)
            
            if not partner.exists() or partner.id in [1, 2, 3, 4, 5, 6]:
                response_data = {
                    'status': 'error',
                    'message': f'Partner with ID {partner_id} not found or cannot be updated',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/update',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Get JSON data from request body
            try:
                raw = request.httprequest.data
                data = json.loads(raw.decode('utf-8'))
            except json.JSONDecodeError as e:
                response_data = {
                    'status': 'error',
                    'message': f'Invalid JSON format: {str(e)}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 400
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/update',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Check if data is empty
            if not data:
                response_data = {
                    'status': 'error',
                    'message': 'No data provided for update',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 400
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/update',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Validate input data
            validation_errors = self._validate_partner_update_data(data)
            if validation_errors:
                response_data = {
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': validation_errors,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 400
                log_status = 'error'
                error_msg = ', '.join(validation_errors)
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/update',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Prepare update values - chỉ các field được phép
            update_vals = {}
            
            # Simple string fields
            simple_fields = ['email', 'phone', 'mobile', 'website', 'vat', 
                           'street', 'street2', 'city', 'zip', 'lang', 'tz']
            
            for field in simple_fields:
                if field in data:
                    update_vals[field] = data[field] if data[field] else False
            
            # Name field - trim whitespace
            if 'name' in data:
                update_vals['name'] = data['name'].strip()
            
            # Relational fields
            if 'state_id' in data:
                update_vals['state_id'] = int(data['state_id']) if data['state_id'] else False
            
            if 'country_id' in data:
                update_vals['country_id'] = int(data['country_id']) if data['country_id'] else False
            
            # Update partner
            partner.write(update_vals)
            
            # Prepare response
            partner_data = self._prepare_partner_data(
                partner,
                include_contacts=False,
                include_addresses=False
            )
            
            response_data = {
                'status': 'success',
                'message': 'Partner updated successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': partner_data,
                'updated_fields': list(update_vals.keys())
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/partners/{partner_id}/update',
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
                'message': f'Failed to update partner: {error_msg}',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/partners/{partner_id}/update: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/partners/{partner_id}/update',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
        
# ====================== 4. DELETE PARTNER (SOFT DELETE) ==================================
    @http.route('/api/v1/partners/<int:partner_id>/delete', type='http', auth='public', methods=['DELETE'], csrf=False, cors='*')
    def delete_partner(self, partner_id, **kwargs):
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
                    endpoint=f'/api/v1/partners/{partner_id}/delete',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            # Check permission for delete
            if not user.api_allow_partner_delete:
                error_msg = "Access denied: You do not have permission to delete partners."
                response_data = {
                    'status': 'error',
                    'message': error_msg,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/delete',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Get partner
            Partner = request.env['res.partner'].sudo()
            partner = Partner.browse(partner_id)
            
            # Check if partner exists
            if not partner.exists():
                response_data = {
                    'status': 'error',
                    'message': f'Partner with ID {partner_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/delete',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            if partner.id in [1, 2, 3, 4, 5, 6]:
                response_data = {
                    'status': 'error',
                    'message': f'Cannot delete partner (ID {partner_id})',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 403
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/delete',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Check if partner is already inactive
            if not partner.active:
                response_data = {
                    'status': 'error',
                    'message': f'Partner with ID {partner_id} is already inactive',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 400
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/delete',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            partner_name = partner.name
            partner_type = partner.type
            
            children = partner.child_ids.filtered(lambda c: c.active)
            
            deactivated_records = []
            
            deactivated_records.append({
                'id': partner.id,
                'name': partner.name,
                'type': partner.type,
                'is_main': True
            })
            
            for child in children:
                deactivated_records.append({
                    'id': child.id,
                    'name': child.name,
                    'type': child.type,
                    'is_main': False
                })
            
            try:
                if children:
                    children.write({'active': False})
                
                partner.write({'active': False})
                
                deactivated_count = 1 + len(children)
                
            except Exception as e:
                error_msg = f"Failed to deactivate partner: {str(e)}"
                response_data = {
                    'status': 'error',
                    'message': error_msg,
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 500
                log_status = 'failed'
                
                _logger.error(f"Error delete partner {partner_id}: {traceback.format_exc()}")
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/partners/{partner_id}/delete',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Prepare success response
            response_data = {
                'status': 'success',
                'message': f'Partner delete successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': {
                    'partner_id': partner_id,
                    'partner_name': partner_name,
                    'partner_type': partner_type,
                    'deactivated_count': deactivated_count,
                    'children_count': len(children),
                    'deactivated_records': deactivated_records
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/partners/{partner_id}/delete',
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
            
            _logger.error(f"API Error at /api/v1/partners/{partner_id}/delete: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/partners/{partner_id}/delete',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)