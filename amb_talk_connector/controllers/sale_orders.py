from odoo import http
from odoo.http import request
from datetime import datetime
import json
import traceback
import logging
from odoo.addons.amb_talk_connector.controllers.main import ApiAuthBaseController

_logger = logging.getLogger(__name__)


class ApiSaleOrderV1Controller(ApiAuthBaseController):
    """API Sale Order Version 1"""
# ====================== 1. ORDER INFOR ==================================
    
    def _build_sale_order_domain(self, filters):
        """Xây dựng domain từ filters cho sale order"""
        domain = []
        
        # Search by name or reference
        if filters.get('search'):
            search_term = filters['search']
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
        # Filter by state
        if filters.get('state'):
            states = filters['state'].split(',') if isinstance(filters['state'], str) else [filters['state']]
            domain.append(('state', 'in', states))
        
        # Filter by partner
        if filters.get('partner_id'):
            try:
                domain.append(('partner_id', '=', int(filters['partner_id'])))
            except ValueError:
                pass
        
        if filters.get('partner_name'):
            domain.append(('partner_id.name', 'ilike', filters['partner_name']))
        
        # Filter by date range
        if filters.get('date_from'):
            domain.append(('date_order', '>=', filters['date_from']))
        
        if filters.get('date_to'):
            domain.append(('date_order', '<=', filters['date_to']))
        
        # Filter by amount range
        if filters.get('amount_min'):
            try:
                domain.append(('amount_total', '>=', float(filters['amount_min'])))
            except ValueError:
                pass
        
        if filters.get('amount_max'):
            try:
                domain.append(('amount_total', '<=', float(filters['amount_max'])))
            except ValueError:
                pass
        
        # Filter by company
        if filters.get('company_id'):
            try:
                domain.append(('company_id', '=', int(filters['company_id'])))
            except ValueError:
                pass
        
        return domain
    
    def _prepare_sale_order_data(self, order, include_lines=False):
        """Chuẩn bị data của sale order"""
        data = {
            'id': order.id,
            'name': order.name,
            'state': order.state,
            'state_display': dict(order._fields['state'].selection).get(order.state),
            'date_order': order.date_order.isoformat() if order.date_order else None,
            'validity_date': order.validity_date.isoformat() if order.validity_date else None,
            'partner': {
                'id': order.partner_id.id,
                'name': order.partner_id.name,
                'email': order.partner_id.email,
                'phone': order.partner_id.phone,
                'vat': order.partner_id.vat,
                'street': order.partner_id.street,
                'street2': order.partner_id.street2,
                'city': order.partner_id.city,
                'state': order.partner_id.state_id.name if order.partner_id.state_id else None,
                'country': order.partner_id.country_id.name if order.partner_id.country_id else None,
                
            } if order.partner_id else None,
            'partner_invoice': {
                'id': order.partner_invoice_id.id,
                'name': order.partner_invoice_id.name,
                'email': order.partner_invoice_id.email,
                'phone': order.partner_invoice_id.phone,
                'vat': order.partner_invoice_id.vat,
                'street': order.partner_invoice_id.street,
                'street2': order.partner_invoice_id.street2,
                'city': order.partner_invoice_id.city,
                'state': order.partner_invoice_id.state_id.name if order.partner_invoice_id.state_id else None,
                'country': order.partner_invoice_id.country_id.name if order.partner_invoice_id.country_id else None,
            } if order.partner_invoice_id else None,
            'partner_shipping': {
                'id': order.partner_shipping_id.id,
                'name': order.partner_shipping_id.name,
                'email': order.partner_shipping_id.email,
                'phone': order.partner_shipping_id.phone,
                'vat': order.partner_shipping_id.vat,
                'street': order.partner_shipping_id.street,
                'street2': order.partner_shipping_id.street2,
                'city': order.partner_shipping_id.city,
                'state': order.partner_shipping_id.state_id.name if order.partner_shipping_id.state_id else None,
                'country': order.partner_shipping_id.country_id.name if order.partner_shipping_id.country_id else None,
            } if order.partner_shipping_id else None,
            
            'company': {
                'id': order.company_id.id,
                'name': order.company_id.name,
            } if order.company_id else None,
            
            'currency': {
                'id': order.currency_id.id,
                'name': order.currency_id.name,
                'symbol': order.currency_id.symbol,
            } if order.currency_id else None,
            
            'amount_untaxed': order.amount_untaxed,
            'amount_tax': order.amount_tax,
            'amount_total': order.amount_total,
            'note': order.note,
            'payment_term': {
                'id': order.payment_term_id.id,
                'name': order.payment_term_id.name,
            } if order.payment_term_id else None,
            
            'create_date': order.create_date.isoformat() if order.create_date else None,
            'write_date': order.write_date.isoformat() if order.write_date else None,
        }
        
        # Include order lines if requested
        if include_lines and order.order_line:
            data['order_lines'] = []
            for line in order.order_line:
                line_data = {
                    'id': line.id,
                    'product': {
                        'id': line.product_id.id,
                        'name': line.product_id.name,
                        'default_code': line.product_id.default_code,
                        # 'barcode': line.product_id.barcode,
                    } if line.product_id else None,
                    'name': line.name,
                    'product_uom_qty': line.product_uom_qty,
                    # 'qty_delivered': line.qty_delivered,
                    # 'qty_invoiced': line.qty_invoiced,
                    'product_uom': {
                        'id': line.product_uom.id,
                        'name': line.product_uom.name,
                    } if line.product_uom else None,
                    'price_unit': line.price_unit,
                    'discount': line.discount,
                    'tax_ids': [{'id': tax.id, 'name': tax.name, 'amount': tax.amount} for tax in line.tax_id],
                    'price_subtotal': line.price_subtotal,
                    'price_total': line.price_total,
                }
                data['order_lines'].append(line_data)
        
        return data
    
    @http.route('/api/v1/sale-orders', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_sale_orders(self, **kwargs):
        """
        Lấy danh sách sale orders với phân trang, search, sort
        
        Query Parameters:
            - page: Số trang (default: 1)
            - page_size: Số records mỗi trang (default: 20, max: 100)
            - limit: Giới hạn số records (alternative to page_size)
            - offset: Bỏ qua số records (alternative to page)
            - sort: Trường sắp xếp (default: date_order)
            - order: Thứ tự sắp xếp: asc/desc (default: desc)
            - search: Tìm kiếm theo name
            - state: Filter theo state (có thể multiple: draft,sent,sale)
            - partner_id: Filter theo partner ID
            - partner_name: Filter theo partner name (like search)
            - user_id: Filter theo salesperson ID
            - date_from: Filter từ ngày (YYYY-MM-DD)
            - date_to: Filter đến ngày (YYYY-MM-DD)
            - amount_min: Filter amount >= giá trị
            - amount_max: Filter amount <= giá trị
            - company_id: Filter theo company
            - include_lines: Có include order lines không (true/false, default: false)
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
                    endpoint='/api/v1/sale-orders',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_sale_order:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/sale-orders',
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
            page_size = min(page_size, 100) 
            offset = int(kwargs.get('offset', (page - 1) * page_size))
            
            # Sort parameters
            sort_field = kwargs.get('sort', 'date_order')
            sort_order = kwargs.get('order', 'desc').lower()
            
            # Validate sort order
            if sort_order not in ['asc', 'desc']:
                sort_order = 'desc'
            
            order_by = f"{sort_field} {sort_order}"
            
            # Build domain from filters
            domain = self._build_sale_order_domain(kwargs)
            
            # Include order lines?
            include_lines = kwargs.get('include_lines', 'false').lower() == 'true'
            
            # Get sale orders
            SaleOrder = request.env['sale.order'].sudo()
            total_count = SaleOrder.search_count(domain)
            orders = SaleOrder.search(domain, limit=page_size, offset=offset, order=order_by)
            
            # Prepare response data
            orders_data = []
            for order in orders:
                try:
                    order_data = self._prepare_sale_order_data(order, include_lines)
                    orders_data.append(order_data)
                except Exception as e:
                    _logger.warning(f"Error preparing data for order {order.id}: {str(e)}")
                    continue
            
            response_data = {
                'status': 'success',
                'message': f'Found {total_count} sale order(s)',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': orders_data,
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
                    'state': kwargs.get('state'),
                    'partner_name': kwargs.get('partner_name'),
                    'date_from': kwargs.get('date_from'),
                    'date_to': kwargs.get('date_to'),
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/sale-orders',
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
            
            _logger.error(f"API Error at /api/v1/sale-orders: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/sale-orders',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/sale-orders/<int:order_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_sale_order_detail(self, order_id, **kwargs):
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
                    endpoint=f'/api/v1/sale-orders/{order_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_sale_order:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/sale-orders/{order_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            # Include order lines by default for detail view
            include_lines = kwargs.get('include_lines', 'true').lower() == 'true'
            
            # Get sale order
            order = request.env['sale.order'].sudo().browse(order_id)
            
            if not order.exists():
                response_data = {
                    'status': 'error',
                    'message': f'Sale order with ID {order_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/sale-orders/{order_id}',
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
            order_data = self._prepare_sale_order_data(order, include_lines)
            
            response_data = {
                'status': 'success',
                'message': 'Sale order retrieved successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': order_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/sale-orders/{order_id}',
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
            
            _logger.error(f"API Error at /api/v1/sale-orders/{order_id}: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/sale-orders/{order_id}',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
        
        
# ====================== 2. CREATE ORDER ==================================
        
    def _validate_order_data(self, data):
        """Validate dữ liệu order trước khi tạo"""
        errors = []
        
        # Validate partner_id (required)
        if not data.get('partner_id'):
            errors.append("partner_id is required")
        else:
            try:
                partner_id = int(data['partner_id'])
                partner = request.env['res.partner'].sudo().browse(partner_id)
                if not partner.exists():
                    errors.append(f"Partner with ID {partner_id} not found")
            except (ValueError, TypeError):
                errors.append("partner_id must be a valid integer")
        
        # Validate order_lines (required)
        if not data.get('order_lines'):
            errors.append("order_lines is required and must contain at least one line")
        elif not isinstance(data['order_lines'], list):
            errors.append("order_lines must be an array")
        elif len(data['order_lines']) == 0:
            errors.append("order_lines must contain at least one line")
        else:
            # Validate each order line
            for idx, line in enumerate(data['order_lines']):
                line_errors = []
                
                # Validate product_id
                if not line.get('product_id'):
                    line_errors.append("product_id is required")
                else:
                    try:
                        product_id = int(line['product_id'])
                        product = request.env['product.product'].sudo().browse(product_id)
                        if not product.exists():
                            line_errors.append(f"Product with ID {product_id} not found")
                        elif not product.sale_ok:
                            line_errors.append(f"Product {product.name} (ID: {product_id}) cannot be sold")
                    except (ValueError, TypeError):
                        line_errors.append("product_id must be a valid integer")
                
                # Validate quantity
                if not line.get('product_uom_qty'):
                    line_errors.append("product_uom_qty is required")
                else:
                    try:
                        qty = float(line['product_uom_qty'])
                        if qty <= 0:
                            line_errors.append("product_uom_qty must be greater than 0")
                    except (ValueError, TypeError):
                        line_errors.append("product_uom_qty must be a valid number")
                
                # Validate price_unit if provided
                if line.get('price_unit') is not None:
                    try:
                        price = float(line['price_unit'])
                        if price < 0:
                            line_errors.append("price_unit must be >= 0")
                    except (ValueError, TypeError):
                        line_errors.append("price_unit must be a valid number")
                
                # Validate discount if provided
                if line.get('discount') is not None:
                    try:
                        discount = float(line['discount'])
                        if discount < 0 or discount > 100:
                            line_errors.append("discount must be between 0 and 100")
                    except (ValueError, TypeError):
                        line_errors.append("discount must be a valid number")
                
                if line_errors:
                    errors.append(f"Line {idx + 1}: {', '.join(line_errors)}")
        
        # Validate user_id if provided
        if data.get('user_id'):
            try:
                user_id = int(data['user_id'])
                user = request.env['res.users'].sudo().browse(user_id)
                if not user.exists():
                    errors.append(f"User with ID {user_id} not found")
            except (ValueError, TypeError):
                errors.append("user_id must be a valid integer")
        
        # Validate payment_term_id if provided
        if data.get('payment_term_id'):
            try:
                payment_term_id = int(data['payment_term_id'])
                payment_term = request.env['account.payment.term'].sudo().browse(payment_term_id)
                if not payment_term.exists():
                    errors.append(f"Payment term with ID {payment_term_id} not found")
            except (ValueError, TypeError):
                errors.append("payment_term_id must be a valid integer")
        
        # Validate date_order if provided
        if data.get('date_order'):
            try:
                datetime.fromisoformat(data['date_order'].replace('Z', '+00:00'))
            except (ValueError, TypeError):
                errors.append("date_order must be in ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # Validate company_id if provided
        if data.get('company_id'):
            try:
                company_id = int(data['company_id'])
                company = request.env['res.company'].sudo().browse(company_id)
                if not company.exists():
                    errors.append(f"Company with ID {company_id} not found")
            except (ValueError, TypeError):
                errors.append("company_id must be a valid integer")
        
        return errors
    
    def _prepare_order_lines_data(self, order_lines):
        """Chuẩn bị data cho order lines"""
        lines_data = []
        
        for line in order_lines:
            product_id = int(line['product_id'])
            product = request.env['product.product'].sudo().browse(product_id)
            
            # Prepare line data
            line_vals = {
                'product_id': product_id,
                'product_uom_qty': float(line['product_uom_qty']),
            }
            
            # Use custom name if provided, otherwise use product name
            if line.get('name'):
                line_vals['name'] = line['name']
            
            # Use custom price if provided, otherwise use product price
            if line.get('price_unit') is not None:
                line_vals['price_unit'] = float(line['price_unit'])
            else:
                line_vals['price_unit'] = product.list_price
            
            # Add discount if provided
            if line.get('discount'):
                line_vals['discount'] = float(line['discount'])
            
            # Add product_uom if provided
            if line.get('product_uom'):
                line_vals['product_uom'] = int(line['product_uom'])
            
            # Add tax_ids if provided
            if line.get('tax_ids'):
                line_vals['tax_id'] = [(6, 0, line['tax_ids'])]
            
            lines_data.append((0, 0, line_vals))
        
        return lines_data
    
    @http.route('/api/v1/sale-orders/create', type='http', auth='public', methods=['POST'], csrf=False, cors='*')
    def create_sale_order(self, **kwargs):
        """
        Tạo mới sale order
        
        Body (JSON):
        {
            "partner_id": 123,                    // Required: Customer ID
            "date_order": "2024-11-25T10:00:00",  // Optional: Order date (ISO format)
            "client_order_ref": "PO-2024-001",    // Optional: Customer Reference
            "user_id": 2,                         // Optional: Salesperson ID
            "payment_term_id": 1,                 // Optional: Payment term ID
            "company_id": 1,                      // Optional: Company ID
            "note": "Special instructions",       // Optional: Internal notes
            "order_lines": [                      // Required: At least 1 line
                {
                    "product_id": 456,            // Required: Product ID
                    "product_uom_qty": 2,         // Required: Quantity
                    "price_unit": 100.00,         // Optional: Unit price (use product price if not provided)
                    "discount": 10,               // Optional: Discount % (0-100)
                    "name": "Custom description", // Optional: Line description
                    "product_uom": 1,             // Optional: UoM ID
                    "tax_ids": [1, 2]            // Optional: Tax IDs array
                },
                ...
            ],
            "confirm_order": true                 // Optional: Auto confirm order after creation (default: false)
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
                    endpoint='/api/v1/sale-orders/create',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_sale_order_create:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/sale-orders/create',
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
                    endpoint='/api/v1/sale-orders/create',
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
            validation_errors = self._validate_order_data(data)
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
                    endpoint='/api/v1/sale-orders/create',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                
                return self._make_response(response_data, status_code)
            
            # Prepare order data
            order_vals = {
                'is_api': True,
                'partner_id': int(data['partner_id']),
            }
            
            # Optional fields
            if data.get('date_order'):
                order_vals['date_order'] = data['date_order']
            
            if data.get('client_order_ref'):
                order_vals['client_order_ref'] = data['client_order_ref']
            
            if data.get('user_id'):
                order_vals['user_id'] = int(data['user_id'])
            
            if data.get('payment_term_id'):
                order_vals['payment_term_id'] = int(data['payment_term_id'])
            
            if data.get('company_id'):
                order_vals['company_id'] = int(data['company_id'])
            
            if data.get('note'):
                order_vals['note'] = data['note']
            
            # Prepare order lines
            order_vals['order_line'] = self._prepare_order_lines_data(data['order_lines'])
            
            # Create sale order
            SaleOrder = request.env['sale.order'].sudo()
            order = SaleOrder.create(order_vals)
            order.message_post(body='Sales order has been created via API.', message_type='comment')
            
            # Auto confirm if requested
            confirm_order = data.get('confirm_order', False)
            if confirm_order:
                try:
                    order.action_confirm()
                except Exception as e:
                    _logger.warning(f"Failed to confirm order {order.id}: {str(e)}")
            
            # Prepare response
            order_data = self._prepare_sale_order_data(order, include_lines=True)
            
            response_data = {
                'status': 'success',
                'message': f'Sale order created successfully{" and confirmed" if confirm_order and order.state != "draft" else ""}',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': order_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/sale-orders/create',
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
                'message': f'Failed to create sale order: {error_msg}',
                'timestamp': datetime.utcnow().isoformat() + "Z"
            }
            log_status = 'failed'
            status_code = 500
            
            _logger.error(f"API Error at /api/v1/sale-orders/create: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/sale-orders/create',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)