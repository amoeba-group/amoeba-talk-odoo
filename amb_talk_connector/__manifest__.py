{
    'name': 'Amoeba Talk Connector',
    'summary': 'REST API connector for Odoo with Bearer token authentication and transaction logging',
    'description': """
Amoeba Talk Connector
=====================

Complete REST API solution for Odoo enabling secure external system integration.

🔐 Authentication & Security
-----------------------------
- Bearer token authentication
- Domain whitelist with wildcard support (*.example.com)
- Granular per-user endpoint permissions
- Complete transaction logging and audit trail

📦 Available Endpoints
----------------------
**Authentication**
- GET /api/v1/auth/check - Verify connection
- GET /api/v1/auth/user-info - Get user information

**Partners (Customers/Suppliers)**
- GET /api/v1/partners - List with pagination & filters
- GET /api/v1/partners/<id> - Get details with contacts
- POST /api/v1/partners/create - Create new partner

**Products**
- GET /api/v1/products - List with search & filters
- GET /api/v1/products/<id> - Get details with stock info

**Sale Orders**
- GET /api/v1/sale-orders - List orders with filters
- GET /api/v1/sale-orders/<id> - Get order with lines
- POST /api/v1/sale-orders/create - Create new order

**Taxes**
- GET /api/v1/taxes - List taxes
- GET /api/v1/taxes/<id> - Get tax details

**Locations**
- GET /api/v1/countries - List countries
- GET /api/v1/states - List states/provinces

✨ Key Features
----------------
- Standard REST format with JSON responses
- Pagination, search, and sorting support
- Comprehensive error handling
- Request/response logging with metadata
- IP tracking and duration measurement
- Per-endpoint permission control

📊 Transaction Logs
-------------------
Track all API requests with:
- User and authentication details
- Request parameters and body
- Response status and data
- Execution time and errors

🎯 Use Cases
------------
- E-commerce integration
- Mobile app backend
- Third-party system sync
- Multi-company/franchise data exchange
- Custom dashboards
- POS integration

📖 Documentation
----------------
Complete setup guide and API documentation available at:
https://github.com/amoeba-group/amoeba-talk-odoo
    """,
    
    'version': '18.0.0.1',
    'category': 'Technical/API',
    'license': 'LGPL-3',
    
    'author': 'Amoeba Group',
    'website': 'https://github.com/amoeba-group/amoeba-talk-odoo',
    'maintainer': 'THUANTL - Amoeba Group',
    'support': 'https://github.com/amoeba-group/amoeba-talk-odoo/issues',
    
    'depends': [
        'base',
        'sale',
        'sale_management',
    ],
    
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/res_users_view.xml',
        'views/api_logs.xml',
    ],
    
    # Images for App Store
    'images': [
        'static/description/amb_talk_18.png',
        'static/description/icon.png',
    ],
    
    # Hooks
    # 'post_init_hook': 'create_api_connect_user',
    
    # Installation
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # Pricing
    'price': 0.00,
    'currency': 'USD',
}