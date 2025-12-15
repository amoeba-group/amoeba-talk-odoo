# Amoeba Talk Connector

[![License: LGPL-3.0](https://img.shields.io/badge/License-LGPL%203.0-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

REST API connector for Odoo - Allows external systems to communicate with Odoo via RESTful APIs.

---

## 📖 What is this module?

This module provides a complete REST API layer for Odoo, enabling external applications (mobile apps, websites, third-party systems) to:
- Retrieve data from Odoo (customers, products, orders, etc.)
- Create new records (customers, sale orders, etc.)
- Authenticate securely using Bearer tokens
- Track all API transactions for security and debugging

## ✨ Features

- ✅ **Secure Authentication** - Token-based API access
- ✅ **Domain Whitelist** - Control which domains can access your API
- ✅ **Transaction Logging** - Complete audit trail of all requests
- ✅ **Granular Permissions** - Control what each user can access
- ✅ **Pagination & Search** - Efficient data retrieval
- ✅ **Standard REST Format** - Easy to integrate with any system

## 📥 Installation

```bash
# Clone to your Odoo addons folder
cd /path/to/odoo/addons
git clone https://github.com/amoeba-group/amoeba-talk-odoo.git amb_talk

# Restart Odoo, then:
# Apps → Update Apps List → Search "Amoeba Talk Connector" → Install
```

## ⚙️ Quick Setup

### Step 1: Generate API Token
1. Go to **Settings → Users**
2. Select a user "User Amoeba Talk Connector" → **API Settings** tab
3. Click **"Generate API Key"**
4. Copy the token (save it securely)

### Step 2: Configure Domain (Optional)
Set which domains can access the API:
```
example.com                    # Single domain
*.example.com                  # All subdomains
example.com, app.example.com   # Multiple domains
*                              # All domains (not recommended)
```

### Step 3: Enable Permissions
Check the endpoints you want to allow for this user.

## 🔌 API Endpoints

All endpoints require: `Authorization: Bearer YOUR_TOKEN`

### 🔐 Authentication

```bash
# Check connection
GET /api/v1/auth/check

# Get user info
GET /api/v1/auth/user-info
```

### 👥 Partners (Customers/Suppliers)

```bash
# List partners
GET /api/v1/partners?page=1&page_size=20&customer=true

# Get partner details
GET /api/v1/partners/7

# Create new partner
POST /api/v1/partners/create
Body: {
  "name": "New Customer",
  "email": "customer@example.com",
  "phone": "+84 123 456 789"
}
```

### 📦 Products

```bash
# List products
GET /api/v1/products?sale_ok=true&page_size=50

# Get product details with stock
GET /api/v1/products/123?include_stock=true&include_suppliers=true
```

### 🛒 Sale Orders

```bash
# List orders
GET /api/v1/sale-orders?state=sale&date_from=2024-01-01

# Get order details
GET /api/v1/sale-orders/456

# Create new order
POST /api/v1/sale-orders/create
Body: {
  "partner_id": 123,
  "order_lines": [
    {
      "product_id": 456,
      "product_uom_qty": 2,
      "price_unit": 100.00
    }
  ],
  "confirm_order": true
}
```

### 💰 Taxes

```bash
# List taxes
GET /api/v1/taxes?type_tax_use=sale

# Get tax details
GET /api/v1/taxes/1
```

### 🌍 Locations

```bash
# List countries
GET /api/v1/countries

# Get country with states
GET /api/v1/countries/233?include_states=true

# List states
GET /api/v1/states?country_id=233

# Get state details
GET /api/v1/states/1
```

## 💡 Usage Example

```bash
# Example: Get list of customers
curl -X GET 'https://your-odoo.com/api/v1/partners?customer=true&page_size=20' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE'
```

**Response:**
```json
{
  "status": "success",
  "message": "Found 50 partner(s)",
  "version": "v1",
  "timestamp": "2024-12-15T10:30:00Z",
  "data": [
    {
      "id": 7,
      "name": "Azure Interior",
      "email": "azure@example.com",
      "phone": "+1 555-0100",
      "is_customer": true
    }
  ],
  "pagination": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "has_next": true
  }
}
```

## 🔍 Common Query Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `page` | Page number | `page=1` |
| `page_size` | Records per page (max 100) | `page_size=20` |
| `sort` | Sort field | `sort=name` |
| `order` | Sort order (asc/desc) | `order=desc` |
| `search` | Search term | `search=john` |

## 📋 Response Format

### Success
```json
{
  "status": "success",
  "message": "Operation successful",
  "version": "v1",
  "timestamp": "2024-12-15T10:30:00Z",
  "data": {...}
}
```

### Error
```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

## 🔑 Permissions

Each endpoint has its own permission flag in **User → API Settings**:

| Permission | Endpoint |
|-----------|----------|
| Allow Partner | `GET /api/v1/partners` |
| Allow Partner Detail | `GET /api/v1/partners/:id` |
| Allow Partner Create | `POST /api/v1/partners/create` |
| Allow Product | `GET /api/v1/products` |
| Allow Product Detail | `GET /api/v1/products/:id` |
| Allow Sale Order | `GET /api/v1/sale-orders` |
| Allow Sale Order Detail | `GET /api/v1/sale-orders/:id` |
| Allow Sale Order Create | `POST /api/v1/sale-orders/create` |
| Allow Tax | `GET /api/v1/taxes` |
| Allow Countries | `GET /api/v1/countries` |
| Allow States | `GET /api/v1/states` |

## 📊 Transaction Logs

View all API requests at: **Settings → Technical → API Transaction Logs**

Logged information:
- Who made the request
- What endpoint was called
- Request parameters and body
- Response status and data
- Execution time
- Errors (if any)

## 🔒 Security Tips

1. ✅ Always use HTTPS in production
2. ✅ Set specific domain whitelist (not `*`)
3. ✅ Rotate API tokens regularly
4. ✅ Enable only necessary permissions
5. ✅ Monitor transaction logs
6. ❌ Never commit tokens to code repositories

## 🔧 Integration Example

### Python
```python
import requests

API_BASE = 'https://your-odoo.com/api/v1'
API_TOKEN = 'your_token_here'

headers = {'Authorization': f'Bearer {API_TOKEN}'}

response = requests.get(f'{API_BASE}/partners', headers=headers)
data = response.json()
```

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/amoeba-group/amoeba-talk-odoo/issues)
- **Documentation:** See inline API documentation in code
- **License:** LGPL-3.0

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

**Made with ❤️ by Amoeba Group**

---
---

# Amoeba Talk Connector (Tiếng Việt)

REST API connector cho Odoo - Cho phép các hệ thống bên ngoài giao tiếp với Odoo thông qua RESTful APIs.

---

## 📖 Module này làm gì?

Module này cung cấp lớp REST API hoàn chỉnh cho Odoo, cho phép các ứng dụng bên ngoài (mobile apps, websites, hệ thống của bên thứ ba) có thể:
- Truy xuất dữ liệu từ Odoo (khách hàng, sản phẩm, đơn hàng, v.v.)
- Tạo mới các bản ghi (khách hàng, đơn hàng bán, v.v.)
- Xác thực an toàn bằng Bearer tokens
- Theo dõi tất cả các giao dịch API để bảo mật và gỡ lỗi

## ✨ Tính năng

- ✅ **Xác thực an toàn** - Truy cập API dựa trên token
- ✅ **Whitelist Domain** - Kiểm soát domain nào có thể truy cập API
- ✅ **Ghi log giao dịch** - Theo dõi đầy đủ tất cả các request
- ✅ **Phân quyền chi tiết** - Kiểm soát những gì mỗi user có thể truy cập
- ✅ **Phân trang & Tìm kiếm** - Truy xuất dữ liệu hiệu quả
- ✅ **Định dạng REST chuẩn** - Dễ dàng tích hợp với bất kỳ hệ thống nào

## 📥 Cài đặt

```bash
# Clone vào thư mục addons của Odoo
cd /path/to/odoo/addons
git clone https://github.com/amoeba-group/amoeba-talk-odoo.git amb_talk

# Khởi động lại Odoo, sau đó:
# Apps → Cập nhật danh sách ứng dụng → Tìm "Amoeba Talk Connector" → Cài đặt
```

## ⚙️ Thiết lập nhanh

### Bước 1: Tạo API Token
1. Vào **Cài đặt → Người dùng**
2. Chọn user "User Amoeba Talk Connector" → Tab **API Settings**
3. Click **"Generate API Key"**
4. Copy token (lưu lại an toàn)

### Bước 2: Cấu hình Domain (Tùy chọn)
Thiết lập domain nào có thể truy cập API:
```
example.com                    # Một domain
*.example.com                  # Tất cả subdomain
example.com, app.example.com   # Nhiều domain
*                              # Tất cả domain (không khuyến nghị)
```

### Bước 3: Bật quyền truy cập
Tick chọn các endpoint mà bạn muốn cho phép user này sử dụng.

## 🔌 Các API Endpoint

Tất cả endpoint yêu cầu: `Authorization: Bearer YOUR_TOKEN`

### 🔐 Xác thực

```bash
# Kiểm tra kết nối
GET /api/v1/auth/check

# Lấy thông tin user
GET /api/v1/auth/user-info
```

### 👥 Đối tác (Khách hàng/Nhà cung cấp)

```bash
# Danh sách đối tác
GET /api/v1/partners?page=1&page_size=20&customer=true

# Chi tiết đối tác
GET /api/v1/partners/7

# Tạo đối tác mới
POST /api/v1/partners/create
Body: {
  "name": "Khách hàng mới",
  "email": "customer@example.com",
  "phone": "+84 123 456 789"
}
```

### 📦 Sản phẩm

```bash
# Danh sách sản phẩm
GET /api/v1/products?sale_ok=true&page_size=50

# Chi tiết sản phẩm với thông tin kho
GET /api/v1/products/123?include_stock=true&include_suppliers=true
```

### 🛒 Đơn hàng bán

```bash
# Danh sách đơn hàng
GET /api/v1/sale-orders?state=sale&date_from=2024-01-01

# Chi tiết đơn hàng
GET /api/v1/sale-orders/456

# Tạo đơn hàng mới
POST /api/v1/sale-orders/create
Body: {
  "partner_id": 123,
  "order_lines": [
    {
      "product_id": 456,
      "product_uom_qty": 2,
      "price_unit": 100.00
    }
  ],
  "confirm_order": true
}
```

### 💰 Thuế

```bash
# Danh sách thuế
GET /api/v1/taxes?type_tax_use=sale

# Chi tiết thuế
GET /api/v1/taxes/1
```

### 🌍 Địa điểm

```bash
# Danh sách quốc gia
GET /api/v1/countries

# Chi tiết quốc gia với tỉnh/thành
GET /api/v1/countries/233?include_states=true

# Danh sách tỉnh/thành
GET /api/v1/states?country_id=233

# Chi tiết tỉnh/thành
GET /api/v1/states/1
```

## 💡 Ví dụ sử dụng

```bash
# Ví dụ: Lấy danh sách khách hàng
curl -X GET 'https://your-odoo.com/api/v1/partners?customer=true&page_size=20' \
  -H 'Authorization: Bearer YOUR_TOKEN_HERE'
```

**Kết quả trả về:**
```json
{
  "status": "success",
  "message": "Found 50 partner(s)",
  "version": "v1",
  "timestamp": "2024-12-15T10:30:00Z",
  "data": [
    {
      "id": 7,
      "name": "Azure Interior",
      "email": "azure@example.com",
      "phone": "+1 555-0100",
      "is_customer": true
    }
  ],
  "pagination": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "has_next": true
  }
}
```

## 🔍 Các tham số truy vấn thường dùng

| Tham số | Mô tả | Ví dụ |
|---------|-------|-------|
| `page` | Số trang | `page=1` |
| `page_size` | Số bản ghi mỗi trang (tối đa 100) | `page_size=20` |
| `sort` | Trường sắp xếp | `sort=name` |
| `order` | Thứ tự sắp xếp (asc/desc) | `order=desc` |
| `search` | Từ khóa tìm kiếm | `search=john` |

## 📋 Định dạng Response

### Thành công
```json
{
  "status": "success",
  "message": "Thao tác thành công",
  "version": "v1",
  "timestamp": "2024-12-15T10:30:00Z",
  "data": {...}
}
```

### Lỗi
```json
{
  "status": "error",
  "message": "Mô tả lỗi",
  "timestamp": "2024-12-15T10:30:00Z"
}
```

## 🔑 Phân quyền

Mỗi endpoint có cờ phân quyền riêng trong **User → API Settings**:

| Quyền | Endpoint |
|-------|----------|
| Allow Partner | `GET /api/v1/partners` |
| Allow Partner Detail | `GET /api/v1/partners/:id` |
| Allow Partner Create | `POST /api/v1/partners/create` |
| Allow Product | `GET /api/v1/products` |
| Allow Product Detail | `GET /api/v1/products/:id` |
| Allow Sale Order | `GET /api/v1/sale-orders` |
| Allow Sale Order Detail | `GET /api/v1/sale-orders/:id` |
| Allow Sale Order Create | `POST /api/v1/sale-orders/create` |
| Allow Tax | `GET /api/v1/taxes` |
| Allow Countries | `GET /api/v1/countries` |
| Allow States | `GET /api/v1/states` |

## 📊 Log giao dịch

Xem tất cả các request API tại: **Cài đặt → Kỹ thuật → API Transaction Logs**

Thông tin được ghi log:
- Ai đã thực hiện request
- Endpoint nào được gọi
- Tham số và nội dung request
- Trạng thái và dữ liệu response
- Thời gian thực thi
- Lỗi (nếu có)

## 🔒 Lưu ý bảo mật

1. ✅ Luôn sử dụng HTTPS trong môi trường production
2. ✅ Thiết lập domain cụ thể (không dùng `*`)
3. ✅ Thay đổi API token định kỳ
4. ✅ Chỉ bật các quyền cần thiết
5. ✅ Theo dõi log giao dịch
6. ❌ Không bao giờ commit token vào code repository

## 🔧 Ví dụ tích hợp

### Python
```python
import requests

API_BASE = 'https://your-odoo.com/api/v1'
API_TOKEN = 'your_token_here'

headers = {'Authorization': f'Bearer {API_TOKEN}'}

response = requests.get(f'{API_BASE}/partners', headers=headers)
data = response.json()
```

## 📞 Hỗ trợ

- **Báo lỗi:** [GitHub Issues](https://github.com/amoeba-group/amoeba-talk-odoo/issues)
- **Tài liệu:** Xem tài liệu inline trong code
- **Giấy phép:** LGPL-3.0

## 🤝 Đóng góp

Chúng tôi hoan nghênh Pull requests! Với các thay đổi lớn, vui lòng mở issue trước.

---

**Made with ❤️ by Amoeba Group**