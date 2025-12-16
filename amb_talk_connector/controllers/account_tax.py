# controllers/api_tax_v1.py
from odoo import http
from odoo.http import request
from datetime import datetime
import json
import traceback
import logging
from odoo.addons.amb_talk_connector.controllers.main import ApiAuthBaseController

_logger = logging.getLogger(__name__)


class ApiTaxV1Controller(ApiAuthBaseController):
    """API Tax Version 1"""
    
    def _build_tax_domain(self, filters):
        """Xây dựng domain từ filters cho tax"""
        domain = []
        
        # Search by name or description
        if filters.get('search'):
            search_term = filters['search']
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
            domain.append(('description', 'ilike', search_term))
        
        # Filter by type_tax_use
        if filters.get('type_tax_use'):
            types = filters['type_tax_use'].split(',') if isinstance(filters['type_tax_use'], str) else [filters['type_tax_use']]
            domain.append(('type_tax_use', 'in', types))
        
        # Filter by amount_type
        if filters.get('amount_type'):
            amount_types = filters['amount_type'].split(',') if isinstance(filters['amount_type'], str) else [filters['amount_type']]
            domain.append(('amount_type', 'in', amount_types))
        
        # Filter by active status
        if filters.get('active'):
            active = filters['active'].lower() in ['true', '1', 'yes']
            domain.append(('active', '=', active))
        else:
            # Default: only active taxes
            domain.append(('active', '=', True))
        
        # Filter by company
        if filters.get('company_id'):
            try:
                domain.append(('company_id', '=', int(filters['company_id'])))
            except ValueError:
                pass
        
        # Filter by amount range
        if filters.get('amount_min'):
            try:
                domain.append(('amount', '>=', float(filters['amount_min'])))
            except ValueError:
                pass
        
        if filters.get('amount_max'):
            try:
                domain.append(('amount', '<=', float(filters['amount_max'])))
            except ValueError:
                pass
        
        # Filter by price_include
        if filters.get('price_include'):
            price_include = filters['price_include'].lower() in ['true', '1', 'yes']
            domain.append(('price_include', '=', price_include))
        
        return domain
    
    def _prepare_tax_data(self, tax, include_children=False):
        """Chuẩn bị data của tax"""
        data = {
            'id': tax.id,
            'name': tax.name,
            'description': tax.description if tax.description else None,
            'type_tax_use': tax.type_tax_use,
            'type_tax_use_display': dict(tax._fields['type_tax_use'].selection).get(tax.type_tax_use),
            'amount_type': tax.amount_type,
            'amount_type_display': dict(tax._fields['amount_type'].selection).get(tax.amount_type),
            'amount': tax.amount,
            'price_include': tax.price_include,
            'include_base_amount': tax.include_base_amount,
            'is_base_affected': tax.is_base_affected if hasattr(tax, 'is_base_affected') else False,
            'active': tax.active,
            'company': {
                'id': tax.company_id.id,
                'name': tax.company_id.name,
            } if tax.company_id else None,
            'tax_group': {
                'id': tax.tax_group_id.id,
                'name': tax.tax_group_id.name,
            } if tax.tax_group_id else None,
            'country': {
                'id': tax.country_id.id,
                'name': tax.country_id.name,
                'code': tax.country_id.code,
            } if tax.country_id else None,
        }
        
        # Include children taxes if requested (for tax groups)
        if include_children and hasattr(tax, 'children_tax_ids') and tax.children_tax_ids:
            data['children_taxes'] = []
            for child_tax in tax.children_tax_ids:
                data['children_taxes'].append({
                    'id': child_tax.id,
                    'name': child_tax.name,
                    'amount': child_tax.amount,
                    'amount_type': child_tax.amount_type,
                })
        
        # Include invoice and refund repartition lines if available
        if hasattr(tax, 'invoice_repartition_line_ids') and tax.invoice_repartition_line_ids:
            data['invoice_repartition'] = []
            for line in tax.invoice_repartition_line_ids:
                data['invoice_repartition'].append({
                    'id': line.id,
                    'factor_percent': line.factor_percent,
                    'repartition_type': line.repartition_type,
                    'account_id': line.account_id.id if line.account_id else None,
                })
        
        if hasattr(tax, 'refund_repartition_line_ids') and tax.refund_repartition_line_ids:
            data['refund_repartition'] = []
            for line in tax.refund_repartition_line_ids:
                data['refund_repartition'].append({
                    'id': line.id,
                    'factor_percent': line.factor_percent,
                    'repartition_type': line.repartition_type,
                    'account_id': line.account_id.id if line.account_id else None,
                })
        
        return data
    
    @http.route('/api/v1/taxes', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_taxes(self, **kwargs):
        """
        Lấy danh sách taxes với phân trang, search, sort
        
        Query Parameters:
            - page: Số trang (default: 1)
            - page_size: Số records mỗi trang (default: 20, max: 100)
            - limit: Giới hạn số records (alternative to page_size)
            - offset: Bỏ qua số records (alternative to page)
            - sort: Trường sắp xếp (default: name)
            - order: Thứ tự sắp xếp: asc/desc (default: asc)
            - search: Tìm kiếm theo name hoặc description
            - type_tax_use: Filter theo type (sale, purchase, none) - có thể multiple
            - amount_type: Filter theo amount type (percent, fixed, division, group) - có thể multiple
            - active: Filter theo active status (true/false, default: true)
            - amount_min: Filter amount >= giá trị
            - amount_max: Filter amount <= giá trị
            - price_include: Filter theo price include (true/false)
            - company_id: Filter theo company
            - include_children: Có include children taxes không (true/false, default: false)
            
        Response:
            {
                "status": "success",
                "message": "Found X tax(es)",
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
                    endpoint='/api/v1/taxes',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_tax:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/taxes',
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
            domain = self._build_tax_domain(kwargs)
            
            # Include children?
            include_children = kwargs.get('include_children', 'false').lower() == 'true'
            
            # Get taxes
            Tax = request.env['account.tax'].sudo()
            total_count = Tax.search_count(domain)
            taxes = Tax.search(domain, limit=page_size, offset=offset, order=order_by)
            
            # Prepare response data
            taxes_data = []
            for tax in taxes:
                try:
                    tax_data = self._prepare_tax_data(tax, include_children=include_children)
                    taxes_data.append(tax_data)
                except Exception as e:
                    _logger.warning(f"Error preparing data for tax {tax.id}: {str(e)}")
                    continue
            
            response_data = {
                'status': 'success',
                'message': f'Found {total_count} tax(es)',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': taxes_data,
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
                    'type_tax_use': kwargs.get('type_tax_use'),
                    'amount_type': kwargs.get('amount_type'),
                    'active': kwargs.get('active', 'true'),
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/taxes',
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
            
            _logger.error(f"API Error at /api/v1/taxes: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/taxes',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/taxes/<int:tax_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_tax_detail(self, tax_id, **kwargs):
        """
        Lấy thông tin chi tiết 1 tax theo ID
        
        URL Parameters:
            - tax_id: ID của tax
            
        Query Parameters:
            - include_children: Có include children taxes không (true/false, default: true)
            
        Response:
            {
                "status": "success",
                "message": "Tax retrieved successfully",
                "version": "v1",
                "timestamp": "2024-11-25T10:00:00Z",
                "data": {
                    "id": 1,
                    "name": "VAT 10%",
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
                    endpoint=f'/api/v1/taxes/{tax_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_tax:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/taxes/{tax_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            # Include children by default for detail view
            include_children = kwargs.get('include_children', 'true').lower() == 'true'
            
            # Get tax
            tax = request.env['account.tax'].sudo().browse(tax_id)
            
            if not tax.exists():
                response_data = {
                    'status': 'error',
                    'message': f'Tax with ID {tax_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/taxes/{tax_id}',
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
            tax_data = self._prepare_tax_data(tax, include_children=include_children)
            
            response_data = {
                'status': 'success',
                'message': 'Tax retrieved successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': tax_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/taxes/{tax_id}',
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
            
            _logger.error(f"API Error at /api/v1/taxes/{tax_id}: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/taxes/{tax_id}',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)