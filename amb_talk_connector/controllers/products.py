from odoo import http
from odoo.http import request
from datetime import datetime
import json
import traceback
import logging
from odoo.addons.amb_auth.controllers.main import ApiAuthBaseController

_logger = logging.getLogger(__name__)


class ApiProductV1Controller(ApiAuthBaseController):
    """API Product Version 1"""
    
    def _build_product_domain(self, filters):
        """Xây dựng domain từ filters cho product"""
        domain = []
        
        # Search by name, default_code (internal reference)
        if filters.get('search'):
            search_term = filters['search']
            domain.append('|')
            domain.append('|')
            domain.append(('name', 'ilike', search_term))
            domain.append(('default_code', 'ilike', search_term))
        
        # Filter by product type
        if filters.get('type'):
            types = filters['type'].split(',') if isinstance(filters['type'], str) else [filters['type']]
            domain.append(('type', 'in', types))
        
        # Filter by category
        if filters.get('categ_id'):
            try:
                domain.append(('categ_id', '=', int(filters['categ_id'])))
            except ValueError:
                pass
        
        if filters.get('categ_name'):
            domain.append(('categ_id.name', 'ilike', filters['categ_name']))
        
        # Filter by sale_ok (can be sold)
        if filters.get('sale_ok'):
            sale_ok = filters['sale_ok'].lower() in ['true', '1', 'yes']
            domain.append(('sale_ok', '=', sale_ok))
        
        # Filter by purchase_ok (can be purchased)
        if filters.get('purchase_ok'):
            purchase_ok = filters['purchase_ok'].lower() in ['true', '1', 'yes']
            domain.append(('purchase_ok', '=', purchase_ok))
        
        
        # Filter by price range (list_price)
        if filters.get('price_min'):
            try:
                domain.append(('list_price', '>=', float(filters['price_min'])))
            except ValueError:
                pass
        
        if filters.get('price_max'):
            try:
                domain.append(('list_price', '<=', float(filters['price_max'])))
            except ValueError:
                pass
        
        # Filter by company
        if filters.get('company_id'):
            try:
                domain.append(('company_id', '=', int(filters['company_id'])))
            except ValueError:
                pass
        
        return domain
    
    def _prepare_product_data(self, product, include_variants=False, include_stock=False, include_suppliers=False):
        """Chuẩn bị data của product"""
        data = {
            'id': product.id,
            'product_tmpl': product.product_tmpl_id.id,
            'name': product.name,
            'display_name': product.display_name,
            'default_code': product.default_code,
            'barcode': product.barcode,
            'type': product.type,
            'type_display': dict(product.product_tmpl_id._fields['type'].selection).get(product.product_tmpl_id.type),
            'categ': {
                'id': product.categ_id.id,
                'name': product.categ_id.name,
                'complete_name': product.categ_id.complete_name,
            } if product.categ_id else None,
            
            'list_price': product.list_price,  
            'standard_price': product.standard_price, 
            
            'currency': {
                'id': product.currency_id.id,
                'name': product.currency_id.name,
                'symbol': product.currency_id.symbol,
            } if product.currency_id else None,
            
            'uom': {
                'id': product.uom_id.id,
                'name': product.uom_id.name,
            } if product.uom_id else None,
            'uom_po': {
                'id': product.uom_po_id.id,
                'name': product.uom_po_id.name,
            } if product.uom_po_id else None,
            
            'sale_ok': product.sale_ok,
            'purchase_ok': product.purchase_ok,
            # 'tracking': product.tracking,
            # 'tracking_display': dict(product._fields['tracking'].selection).get(product.tracking),
            'weight': product.weight,
            'volume': product.volume,
            'description': product.description,
            'description_sale': product.description_sale,
            'description_purchase': product.description_purchase,
            'company': {
                'id': product.company_id.id,
                'name': product.company_id.name,
            } if product.company_id else None,
            'create_date': product.create_date.isoformat() if product.create_date else None,
            'write_date': product.write_date.isoformat() if product.write_date else None,
        }
        
        # Include product variants/attributes
        if include_variants and hasattr(product, 'product_template_attribute_value_ids'):
            data['attributes'] = []
            for attr_value in product.product_template_attribute_value_ids:
                data['attributes'].append({
                    'attribute_name': attr_value.attribute_id.name,
                    'value_name': attr_value.name,
                })
        
        # Include stock information
        try:
            if include_stock:
                data['stock_info'] = {
                    'qty_available': product.qty_available,  # Quantity On Hand
                    'virtual_available': product.virtual_available,  # Forecast Quantity
                    'incoming_qty': product.incoming_qty,
                    'outgoing_qty': product.outgoing_qty,
                }
        except Exception as e: 
            pass
            
        # Include suppliers information
        if include_suppliers and hasattr(product, 'seller_ids') and product.seller_ids:
            data['suppliers'] = []
            for seller in product.seller_ids:
                data['suppliers'].append({
                    'id': seller.id,
                    'partner': {
                        'id': seller.partner_id.id,
                        'name': seller.partner_id.name,
                    } if seller.partner_id else None,
                    'product_name': seller.product_name,
                    'product_code': seller.product_code,
                    'price': seller.price,
                    'min_qty': seller.min_qty,
                    'delay': seller.delay,
                    'currency': {
                        'id': seller.currency_id.id,
                        'name': seller.currency_id.name,
                        'symbol': seller.currency_id.symbol,
                    } if seller.currency_id else None,
                })
        
        # Include taxes
        if hasattr(product, 'taxes_id') and product.taxes_id:
            data['taxes'] = [{'id': tax.id, 'name': tax.name, 'amount': tax.amount} for tax in product.taxes_id]
        
        if hasattr(product, 'supplier_taxes_id') and product.supplier_taxes_id:
            data['supplier_taxes'] = [{'id': tax.id, 'name': tax.name, 'amount': tax.amount} for tax in product.supplier_taxes_id]
        
        return data
    
    @http.route('/api/v1/products', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_products(self, **kwargs):
        """
        Lấy danh sách products với phân trang, search, sort
        
        Query Parameters:
            - page: Số trang (default: 1)
            - page_size: Số records mỗi trang (default: 20, max: 100)
            - limit: Giới hạn số records (alternative to page_size)
            - offset: Bỏ qua số records (alternative to page)
            - sort: Trường sắp xếp (default: name)
            - order: Thứ tự sắp xếp: asc/desc (default: asc)
            - search: Tìm kiếm theo name, default_code, hoặc barcode
            - type: Filter theo type (consu, service, product)
            - categ_id: Filter theo category ID
            - categ_name: Filter theo category name (like search)
            - sale_ok: Filter theo can be sold (true/false)
            - purchase_ok: Filter theo can be purchased (true/false)
            - active: Filter theo active status (true/false, default: true)
            - price_min: Filter price >= giá trị
            - price_max: Filter price <= giá trị
            - company_id: Filter theo company
            - tracking: Filter theo tracking (none, lot, serial)
            - include_variants: Có include product variants/attributes không (true/false, default: false)
            - include_stock: Có include stock info không (true/false, default: false)
            - include_suppliers: Có include suppliers không (true/false, default: false)
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
                    endpoint='/api/v1/products',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_product:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint='/api/v1/products',
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
            domain = self._build_product_domain(kwargs)
            
            # Include options
            include_variants = kwargs.get('include_variants', 'false').lower() == 'true'
            include_stock = kwargs.get('include_stock', 'false').lower() == 'true'
            include_suppliers = kwargs.get('include_suppliers', 'false').lower() == 'true'
            
            # Get products
            Product = request.env['product.product'].sudo()
            total_count = Product.search_count(domain)
            products = Product.search(domain, limit=page_size, offset=offset, order=order_by)
            
            # Prepare response data
            products_data = []
            for product in products:
                try:
                    product_data = self._prepare_product_data(
                        product, 
                        include_variants=include_variants,
                        include_stock=include_stock,
                        include_suppliers=include_suppliers
                    )
                    products_data.append(product_data)
                except Exception as e:
                    _logger.warning(f"Error preparing data for product {product.id}: {str(e)}")
                    continue
            
            response_data = {
                'status': 'success',
                'message': f'Found {total_count} product(s)',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': products_data,
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
                    'categ_name': kwargs.get('categ_name'),
                    'sale_ok': kwargs.get('sale_ok'),
                    'purchase_ok': kwargs.get('purchase_ok'),
                }
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint='/api/v1/products',
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
            
            _logger.error(f"API Error at /api/v1/products: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint='/api/v1/products',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)
    
    @http.route('/api/v1/products/<int:product_id>', type='http', auth='public', methods=['GET'], csrf=False, cors='*')
    def get_product_detail(self, product_id, **kwargs):
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
                    endpoint=f'/api/v1/products/{product_id}',
                    version='v1',
                    user=user,
                    response_data=response_data,
                    status=log_status,
                    response_status=status_code,
                    error_message=error_msg,
                    start_time=start_time
                )
                return self._make_response(response_data, status_code)
            
            if not user.api_allow_product_detail:
                error_msg = "Access denied: You do not have permission to access this endpoint."
                response_data = {
                    'status': 'error',
                    'message': f'{error_msg}',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                log_status = 'failed'
                status_code = 403
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/products/{product_id}',
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
            include_variants = kwargs.get('include_variants', 'false').lower() == 'true'
            include_stock = kwargs.get('include_stock', 'false').lower() == 'true'
            include_suppliers = kwargs.get('include_suppliers', 'false').lower() == 'true'
            
            # Get product
            product = request.env['product.product'].sudo().browse(product_id)
            
            if not product.exists():
                response_data = {
                    'status': 'error',
                    'message': f'Product with ID {product_id} not found',
                    'timestamp': datetime.utcnow().isoformat() + "Z"
                }
                status_code = 404
                log_status = 'error'
                error_msg = response_data['message']
                
                self._create_transaction_log(
                    endpoint=f'/api/v1/products/{product_id}',
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
            product_data = self._prepare_product_data(
                product,
                include_variants=include_variants,
                include_stock=include_stock,
                include_suppliers=include_suppliers
            )
            
            response_data = {
                'status': 'success',
                'message': 'Product retrieved successfully',
                'version': 'v1',
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'data': product_data
            }
            
            # Log successful transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/products/{product_id}',
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
            
            _logger.error(f"API Error at /api/v1/products/{product_id}: {traceback.format_exc()}")
            
            # Log failed transaction
            self._create_transaction_log(
                endpoint=f'/api/v1/products/{product_id}',
                version='v1',
                user=user,
                response_data=response_data,
                status=log_status,
                response_status=status_code,
                error_message=error_msg,
                start_time=start_time
            )
            
            return self._make_response(response_data, status_code)