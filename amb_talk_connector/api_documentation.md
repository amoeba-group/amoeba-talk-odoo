# Tài Liệu API - AMB Talk Connector v1

## Tổng Quan

API này cung cấp các endpoint RESTful để tích hợp hệ thống bên ngoài với Odoo 18. Tất cả endpoint đều sử dụng xác thực bằng token và trả về response dạng JSON.

**Base URL**: `https://your-domain.com`

**Phiên bản**: v1

---

## Xác Thực

### Headers Bắt Buộc
```
Authorization: Bearer YOUR_API_TOKEN
```

### Định Dạng Response Chuẩn
```json
{
    "status": "success|error",
    "message": "Mô tả thông báo",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {...},
    "pagination": {...}
}
```

### Mã HTTP Status
- `200` - Thành công
- `400` - Request không hợp lệ
- `401` - Chưa xác thực
- `403` - Không có quyền
- `404` - Không tìm thấy
- `500` - Lỗi máy chủ

---

## 1. API THUẾ

### 1.1. Lấy Danh Sách Thuế

Lấy danh sách các loại thuế với phân trang, tìm kiếm và sắp xếp.

**Endpoint**: `GET /api/v1/taxes`

**Quyền**: `api_allow_tax`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 20 | Số bản ghi mỗi trang (tối đa: 100) |
| `limit` | integer | Không | 20 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | name | Trường sắp xếp |
| `order` | string | Không | asc | Thứ tự: `asc` hoặc `desc` |
| `search` | string | Không | - | Tìm kiếm trong tên hoặc mô tả |
| `type_tax_use` | string | Không | - | Lọc theo loại: `sale`, `purchase`, `none` (ngăn cách bằng dấu phẩy) |
| `amount_type` | string | Không | - | Lọc theo kiểu: `percent`, `fixed`, `division`, `group` |
| `active` | boolean | Không | true | Lọc theo trạng thái hoạt động |
| `amount_min` | float | Không | - | Thuế suất tối thiểu |
| `amount_max` | float | Không | - | Thuế suất tối đa |
| `price_include` | boolean | Không | - | Giá đã bao gồm thuế |
| `company_id` | integer | Không | - | Lọc theo công ty |
| `include_children` | boolean | Không | false | Bao gồm thuế con |

#### Ví Dụ Request

```bash
GET /api/v1/taxes?page=1&page_size=20&type_tax_use=sale&active=true&sort=amount&order=desc
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 10 thuế",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 1,
            "name": "VAT 10%",
            "description": "Thuế giá trị gia tăng 10%",
            "type_tax_use": "sale",
            "type_tax_use_display": "Bán hàng",
            "amount_type": "percent",
            "amount_type_display": "Phần trăm giá",
            "amount": 10.0,
            "price_include": false,
            "include_base_amount": false,
            "active": true,
            "company": {
                "id": 1,
                "name": "Công ty của tôi"
            },
            "tax_group": {
                "id": 1,
                "name": "Thuế"
            },
            "country": {
                "id": 233,
                "name": "Vietnam",
                "code": "VN"
            }
        }
    ],
    "pagination": {
        "total": 10,
        "page": 1,
        "page_size": 20,
        "total_pages": 1,
        "offset": 0,
        "has_next": false,
        "has_previous": false
    },
    "filters_applied": {
        "search": null,
        "type_tax_use": "sale",
        "amount_type": null,
        "active": "true"
    }
}
```

---

### 1.2. Lấy Chi Tiết Thuế

Lấy thông tin chi tiết của một loại thuế theo ID.

**Endpoint**: `GET /api/v1/taxes/{tax_id}`

**Quyền**: `api_allow_tax`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `tax_id` | integer | Có | ID thuế |

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `include_children` | boolean | Không | true | Bao gồm thuế con |

#### Ví Dụ Request

```bash
GET /api/v1/taxes/1?include_children=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin thuế thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 1,
        "name": "VAT 10%",
        "description": "Thuế giá trị gia tăng 10%",
        "type_tax_use": "sale",
        "type_tax_use_display": "Bán hàng",
        "amount_type": "percent",
        "amount_type_display": "Phần trăm giá",
        "amount": 10.0,
        "price_include": false,
        "include_base_amount": false,
        "is_base_affected": false,
        "active": true,
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "tax_group": {
            "id": 1,
            "name": "Thuế"
        },
        "country": {
            "id": 233,
            "name": "Vietnam",
            "code": "VN"
        },
        "children_taxes": [
            {
                "id": 2,
                "name": "Thuế thành phố",
                "amount": 2.0,
                "amount_type": "percent"
            }
        ],
        "invoice_repartition": [
            {
                "id": 1,
                "factor_percent": 100.0,
                "repartition_type": "tax",
                "account_id": 10
            }
        ],
        "refund_repartition": [
            {
                "id": 2,
                "factor_percent": 100.0,
                "repartition_type": "tax",
                "account_id": 10
            }
        ]
    }
}
```

---

## 2. API SẢN PHẨM

### 2.1. Lấy Danh Sách Sản Phẩm (Product Variant)

Lấy danh sách các biến thể sản phẩm với phân trang, tìm kiếm và lọc.

**Endpoint**: `GET /api/v1/products`

**Quyền**: `api_allow_product`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 20 | Số bản ghi mỗi trang (tối đa: 100) |
| `limit` | integer | Không | 20 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | name | Trường sắp xếp |
| `order` | string | Không | asc | Thứ tự sắp xếp |
| `search` | string | Không | - | Tìm trong tên, mã sản phẩm |
| `type` | string | Không | - | Loại: `consu`, `service`, `product` (ngăn cách bằng dấu phẩy) |
| `categ_id` | integer | Không | - | ID danh mục |
| `categ_name` | string | Không | - | Tên danh mục (tìm gần đúng) |
| `sale_ok` | boolean | Không | - | Có thể bán |
| `purchase_ok` | boolean | Không | - | Có thể mua |
| `price_min` | float | Không | - | Giá tối thiểu |
| `price_max` | float | Không | - | Giá tối đa |
| `company_id` | integer | Không | - | ID công ty |
| `include_variants` | boolean | Không | false | Bao gồm thuộc tính biến thể |
| `include_stock` | boolean | Không | false | Bao gồm thông tin tồn kho |
| `include_suppliers` | boolean | Không | false | Bao gồm nhà cung cấp |

#### Ví Dụ Request

```bash
GET /api/v1/products?page=1&page_size=10&sale_ok=true&type=product&include_stock=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 50 sản phẩm",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 1,
            "product_tmpl": 1,
            "name": "Laptop Dell XPS 13",
            "display_name": "Laptop Dell XPS 13",
            "default_code": "LAPTOP-001",
            "barcode": "1234567890123",
            "type": "product",
            "type_display": "Sản phẩm tồn kho",
            "categ": {
                "id": 1,
                "name": "Điện tử",
                "complete_name": "Tất cả / Điện tử"
            },
            "list_price": 1200.00,
            "standard_price": 800.00,
            "currency": {
                "id": 1,
                "name": "USD",
                "symbol": "$"
            },
            "uom": {
                "id": 1,
                "name": "Cái"
            },
            "uom_po": {
                "id": 1,
                "name": "Cái"
            },
            "sale_ok": true,
            "purchase_ok": true,
            "weight": 1.2,
            "volume": 0.05,
            "description": "Laptop cao cấp",
            "description_sale": "Laptop Dell XPS 13 - hiệu năng cao",
            "description_purchase": "Laptop Dell XPS 13 để mua hàng",
            "company": {
                "id": 1,
                "name": "Công ty của tôi"
            },
            "stock_info": {
                "qty_available": 50.0,
                "virtual_available": 45.0,
                "incoming_qty": 10.0,
                "outgoing_qty": 15.0
            },
            "taxes": [
                {
                    "id": 1,
                    "name": "VAT 10%",
                    "amount": 10.0
                }
            ],
            "supplier_taxes": [],
            "create_date": "2024-01-01T00:00:00",
            "write_date": "2024-11-25T10:00:00"
        }
    ],
    "pagination": {
        "total": 50,
        "page": 1,
        "page_size": 10,
        "total_pages": 5,
        "offset": 0,
        "has_next": true,
        "has_previous": false
    },
    "filters_applied": {
        "search": null,
        "type": "product",
        "categ_name": null,
        "sale_ok": "true",
        "purchase_ok": null
    }
}
```

---

### 2.2. Lấy Chi Tiết Sản Phẩm

Lấy thông tin chi tiết của một sản phẩm theo ID.

**Endpoint**: `GET /api/v1/products/{product_id}`

**Quyền**: `api_allow_product`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `product_id` | integer | Có | ID sản phẩm |

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `include_variants` | boolean | Không | false | Bao gồm thuộc tính biến thể |
| `include_stock` | boolean | Không | false | Bao gồm thông tin tồn kho |
| `include_suppliers` | boolean | Không | false | Bao gồm nhà cung cấp |

#### Ví Dụ Request

```bash
GET /api/v1/products/1?include_stock=true&include_suppliers=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin sản phẩm thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 1,
        "product_tmpl": 1,
        "name": "Laptop Dell XPS 13",
        "display_name": "Laptop Dell XPS 13",
        "default_code": "LAPTOP-001",
        "barcode": "1234567890123",
        "type": "product",
        "type_display": "Sản phẩm tồn kho",
        "categ": {
            "id": 1,
            "name": "Điện tử",
            "complete_name": "Tất cả / Điện tử"
        },
        "list_price": 1200.00,
        "standard_price": 800.00,
        "currency": {
            "id": 1,
            "name": "USD",
            "symbol": "$"
        },
        "uom": {
            "id": 1,
            "name": "Cái"
        },
        "uom_po": {
            "id": 1,
            "name": "Cái"
        },
        "sale_ok": true,
        "purchase_ok": true,
        "weight": 1.2,
        "volume": 0.05,
        "description": "Laptop cao cấp",
        "stock_info": {
            "qty_available": 50.0,
            "virtual_available": 45.0,
            "incoming_qty": 10.0,
            "outgoing_qty": 15.0
        },
        "suppliers": [
            {
                "id": 1,
                "partner": {
                    "id": 10,
                    "name": "Nhà cung cấp A"
                },
                "product_name": "Dell XPS 13",
                "product_code": "DELL-XPS13",
                "price": 750.00,
                "min_qty": 1.0,
                "delay": 7,
                "currency": {
                    "id": 1,
                    "name": "USD",
                    "symbol": "$"
                }
            }
        ],
        "taxes": [
            {
                "id": 1,
                "name": "VAT 10%",
                "amount": 10.0
            }
        ],
        "create_date": "2024-01-01T00:00:00",
        "write_date": "2024-11-25T10:00:00"
    }
}
```

---

### 2.3. Lấy Danh Sách Product Template

Lấy danh sách các template sản phẩm (sản phẩm gốc).

**Endpoint**: `GET /api/v1/product-templates`

**Quyền**: `api_allow_product_template`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 20 | Số bản ghi mỗi trang (tối đa: 100) |
| `limit` | integer | Không | 20 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | name | Trường sắp xếp |
| `order` | string | Không | asc | Thứ tự sắp xếp |
| `search` | string | Không | - | Tìm trong tên, mã |
| `type` | string | Không | - | Loại: `consu`, `service`, `product` |
| `categ_id` | integer | Không | - | ID danh mục |
| `categ_name` | string | Không | - | Tên danh mục |
| `sale_ok` | boolean | Không | - | Có thể bán |
| `purchase_ok` | boolean | Không | - | Có thể mua |
| `active` | boolean | Không | - | Đang hoạt động |
| `price_min` | float | Không | - | Giá tối thiểu |
| `price_max` | float | Không | - | Giá tối đa |
| `company_id` | integer | Không | - | ID công ty |
| `include_variants` | boolean | Không | false | Bao gồm tất cả biến thể |
| `include_stock` | boolean | Không | false | Bao gồm tồn kho |
| `include_suppliers` | boolean | Không | false | Bao gồm nhà cung cấp |

#### Ví Dụ Request

```bash
GET /api/v1/product-templates?page=1&sale_ok=true&include_variants=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 30 product template",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 1,
            "name": "Áo thun",
            "display_name": "Áo thun",
            "default_code": "SHIRT-001",
            "barcode": null,
            "type": "product",
            "type_display": "Sản phẩm tồn kho",
            "categ": {
                "id": 2,
                "name": "Quần áo",
                "complete_name": "Tất cả / Quần áo"
            },
            "list_price": 100.00,
            "standard_price": 50.00,
            "currency": {
                "id": 1,
                "name": "USD",
                "symbol": "$"
            },
            "uom": {
                "id": 1,
                "name": "Cái"
            },
            "uom_po": {
                "id": 1,
                "name": "Cái"
            },
            "sale_ok": true,
            "purchase_ok": true,
            "active": true,
            "tracking": "none",
            "tracking_display": "Không theo dõi",
            "weight": 0.2,
            "volume": 0.01,
            "description": "Áo thun cotton",
            "company": {
                "id": 1,
                "name": "Công ty của tôi"
            },
            "product_variant_count": 6,
            "has_configurable_attributes": true,
            "variants": [
                {
                    "id": 10,
                    "display_name": "Áo thun (Đỏ, L)",
                    "default_code": "SHIRT-001-R-L",
                    "barcode": null,
                    "list_price": 100.00,
                    "standard_price": 50.00,
                    "active": true,
                    "attributes": [
                        {
                            "attribute_id": 1,
                            "attribute_name": "Màu sắc",
                            "value_id": 1,
                            "value_name": "Đỏ"
                        },
                        {
                            "attribute_id": 2,
                            "attribute_name": "Kích thước",
                            "value_id": 3,
                            "value_name": "L"
                        }
                    ]
                },
                {
                    "id": 11,
                    "display_name": "Áo thun (Xanh, M)",
                    "default_code": "SHIRT-001-B-M",
                    "barcode": null,
                    "list_price": 100.00,
                    "standard_price": 50.00,
                    "active": true,
                    "attributes": [
                        {
                            "attribute_id": 1,
                            "attribute_name": "Màu sắc",
                            "value_id": 2,
                            "value_name": "Xanh"
                        },
                        {
                            "attribute_id": 2,
                            "attribute_name": "Kích thước",
                            "value_id": 2,
                            "value_name": "M"
                        }
                    ]
                }
            ],
            "attribute_lines": [
                {
                    "id": 1,
                    "attribute": {
                        "id": 1,
                        "name": "Màu sắc",
                        "display_type": "color"
                    },
                    "values": [
                        {"id": 1, "name": "Đỏ"},
                        {"id": 2, "name": "Xanh"}
                    ]
                },
                {
                    "id": 2,
                    "attribute": {
                        "id": 2,
                        "name": "Kích thước",
                        "display_type": "radio"
                    },
                    "values": [
                        {"id": 1, "name": "S"},
                        {"id": 2, "name": "M"},
                        {"id": 3, "name": "L"}
                    ]
                }
            ],
            "taxes": [
                {
                    "id": 1,
                    "name": "VAT 10%",
                    "amount": 10.0
                }
            ],
            "has_image": true,
            "create_date": "2024-01-01T00:00:00",
            "write_date": "2024-11-25T10:00:00"
        }
    ],
    "pagination": {
        "total": 30,
        "page": 1,
        "page_size": 20,
        "total_pages": 2,
        "offset": 0,
        "has_next": true,
        "has_previous": false
    }
}
```

---

### 2.4. Lấy Chi Tiết Product Template

Lấy thông tin chi tiết của một product template theo ID.

**Endpoint**: `GET /api/v1/product-templates/{template_id}`

**Quyền**: `api_allow_product_template`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `template_id` | integer | Có | ID product template |

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `include_variants` | boolean | Không | true | Bao gồm tất cả biến thể |
| `include_stock` | boolean | Không | true | Bao gồm thông tin tồn kho |
| `include_suppliers` | boolean | Không | true | Bao gồm nhà cung cấp |

#### Ví Dụ Request

```bash
GET /api/v1/product-templates/1?include_variants=true&include_stock=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin product template thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 1,
        "name": "Áo thun",
        "display_name": "Áo thun",
        "default_code": "SHIRT-001",
        "type": "product",
        "type_display": "Sản phẩm tồn kho",
        "categ": {
            "id": 2,
            "name": "Quần áo",
            "complete_name": "Tất cả / Quần áo"
        },
        "list_price": 100.00,
        "standard_price": 50.00,
        "sale_ok": true,
        "purchase_ok": true,
        "active": true,
        "product_variant_count": 6,
        "has_configurable_attributes": true,
        "variants": [
            {
                "id": 10,
                "display_name": "Áo thun (Đỏ, L)",
                "list_price": 100.00,
                "attributes": [
                    {
                        "attribute_id": 1,
                        "attribute_name": "Màu sắc",
                        "value_id": 1,
                        "value_name": "Đỏ"
                    }
                ],
                "stock_info": {
                    "qty_available": 25.0,
                    "virtual_available": 20.0,
                    "incoming_qty": 5.0,
                    "outgoing_qty": 10.0
                }
            }
        ],
        "attribute_lines": [
            {
                "id": 1,
                "attribute": {
                    "id": 1,
                    "name": "Màu sắc",
                    "display_type": "color"
                },
                "values": [
                    {"id": 1, "name": "Đỏ"},
                    {"id": 2, "name": "Xanh"}
                ]
            }
        ],
        "stock_info": {
            "total_qty_available": 150.0,
            "total_virtual_available": 120.0
        },
        "create_date": "2024-01-01T00:00:00"
    }
}
```

---

## 3. API ĐỊA ĐIỂM

### 3.1. Lấy Danh Sách Quốc Gia

Lấy danh sách các quốc gia.

**Endpoint**: `GET /api/v1/countries`

**Quyền**: `api_allow_countries`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 50 | Số bản ghi mỗi trang (tối đa: 250) |
| `limit` | integer | Không | 50 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | name | Trường sắp xếp |
| `order` | string | Không | asc | Thứ tự sắp xếp |
| `search` | string | Không | - | Tìm trong tên hoặc mã |
| `code` | string | Không | - | Mã quốc gia (VN, US, ...) |
| `phone_code` | string | Không | - | Mã điện thoại (84, 1, ...) |
| `include_states` | boolean | Không | false | Bao gồm tỉnh/thành |

#### Ví Dụ Request

```bash
GET /api/v1/countries?search=vietnam&include_states=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 1 quốc gia",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 233,
            "name": "Vietnam",
            "code": "VN",
            "phone_code": "84",
            "currency": {
                "id": 23,
                "name": "VND",
                "symbol": "₫"
            },
            "image_url": "/web/image/res.country/233/image_512",
            "states": [
                {
                    "id": 1,
                    "name": "Hồ Chí Minh",
                    "code": "SG"
                },
                {
                    "id": 2,
                    "name": "Hà Nội",
                    "code": "HN"
                },
                {
                    "id": 3,
                    "name": "Đà Nẵng",
                    "code": "DN"
                }
            ]
        }
    ],
    "pagination": {
        "total": 1,
        "page": 1,
        "page_size": 50,
        "total_pages": 1,
        "offset": 0,
        "has_next": false,
        "has_previous": false
    },
    "filters_applied": {
        "search": "vietnam",
        "code": null,
        "phone_code": null
    }
}
```

---

### 3.2. Lấy Chi Tiết Quốc Gia

Lấy thông tin chi tiết của một quốc gia theo ID.

**Endpoint**: `GET /api/v1/countries/{country_id}`

**Quyền**: `api_allow_countries`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `country_id` | integer | Có | ID quốc gia |

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `include_states` | boolean | Không | true | Bao gồm tỉnh/thành |

#### Ví Dụ Request

```bash
GET /api/v1/countries/233?include_states=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin quốc gia thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 233,
        "name": "Vietnam",
        "code": "VN",
        "phone_code": "84",
        "currency": {
            "id": 23,
            "name": "VND",
            "symbol": "₫"
        },
        "image_url": "/web/image/res.country/233/image_512",
        "states": [
            {
                "id": 1,
                "name": "Hồ Chí Minh",
                "code": "SG"
            },
            {
                "id": 2,
                "name": "Hà Nội",
                "code": "HN"
            },
            {
                "id": 3,
                "name": "Đà Nẵng",
                "code": "DN"
            },
            {
                "id": 4,
                "name": "Cần Thơ",
                "code": "CT"
            }
        ]
    }
}
```

---

### 3.3. Lấy Danh Sách Tỉnh/Thành

Lấy danh sách các tỉnh/thành phố.

**Endpoint**: `GET /api/v1/states`

**Quyền**: `api_allow_states`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 50 | Số bản ghi mỗi trang (tối đa: 500) |
| `limit` | integer | Không | 50 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | name | Trường sắp xếp |
| `order` | string | Không | asc | Thứ tự sắp xếp |
| `search` | string | Không | - | Tìm trong tên hoặc mã |
| `country_id` | integer | Không | - | Lọc theo ID quốc gia (khuyến nghị) |
| `country_code` | string | Không | - | Lọc theo mã quốc gia |
| `code` | string | Không | - | Mã tỉnh/thành |

#### Ví Dụ Request

```bash
GET /api/v1/states?country_id=233&page_size=100
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 63 tỉnh/thành",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 1,
            "name": "Hồ Chí Minh",
            "code": "SG",
            "country": {
                "id": 233,
                "name": "Vietnam",
                "code": "VN"
            }
        },
        {
            "id": 2,
            "name": "Hà Nội",
            "code": "HN",
            "country": {
                "id": 233,
                "name": "Vietnam",
                "code": "VN"
            }
        },
        {
            "id": 3,
            "name": "Đà Nẵng",
            "code": "DN",
            "country": {
                "id": 233,
                "name": "Vietnam",
                "code": "VN"
            }
        }
    ],
    "pagination": {
        "total": 63,
        "page": 1,
        "page_size": 100,
        "total_pages": 1,
        "offset": 0,
        "has_next": false,
        "has_previous": false
    },
    "filters_applied": {
        "search": null,
        "country_id": "233",
        "country_code": null,
        "code": null
    }
}
```

---

### 3.4. Lấy Chi Tiết Tỉnh/Thành

Lấy thông tin chi tiết của một tỉnh/thành theo ID.

**Endpoint**: `GET /api/v1/states/{state_id}`

**Quyền**: `api_allow_states`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `state_id` | integer | Có | ID tỉnh/thành |

#### Query Parameters

Không có query parameters.

#### Ví Dụ Request

```bash
GET /api/v1/states/1
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin tỉnh/thành thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 1,
        "name": "Hồ Chí Minh",
        "code": "SG",
        "country": {
            "id": 233,
            "name": "Vietnam",
            "code": "VN"
        }
    }
}
```

---

## 4. API ĐỐI TÁC

### 4.1. Lấy Danh Sách Đối Tác

Lấy danh sách khách hàng, nhà cung cấp, liên hệ.

**Endpoint**: `GET /api/v1/partners`

**Quyền**: `api_allow_partner`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 20 | Số bản ghi mỗi trang (tối đa: 100) |
| `limit` | integer | Không | 20 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | name | Trường sắp xếp |
| `order` | string | Không | asc | Thứ tự sắp xếp |
| `search` | string | Không | - | Tìm trong tên, email, điện thoại, mã số thuế |
| `type` | string | Không | - | Loại: `contact`, `invoice`, `delivery`, `other`, `private` |
| `is_company` | boolean | Không | - | Là công ty |
| `customer` | boolean | Không | - | Là khách hàng |
| `supplier` | boolean | Không | - | Là nhà cung cấp |
| `active` | boolean | Không | true | Đang hoạt động |
| `parent_id` | integer | Không | - | ID đối tác cha |
| `has_parent` | boolean | Không | - | Có đối tác cha hay không |
| `country_id` | integer | Không | - | ID quốc gia |
| `country_code` | string | Không | - | Mã quốc gia |
| `state_id` | integer | Không | - | ID tỉnh/thành |
| `city` | string | Không | - | Thành phố |
| `company_id` | integer | Không | - | ID công ty |
| `category_id` | integer | Không | - | ID nhóm đối tác |
| `include_contacts` | boolean | Không | false | Bao gồm liên hệ con |
| `include_addresses` | boolean | Không | false | Bao gồm địa chỉ |

#### Ví Dụ Request

```bash
GET /api/v1/partners?customer=true&country_code=VN&include_contacts=true&page=1&page_size=20
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 100 đối tác",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 7,
            "name": "Công ty Azure Interior",
            "display_name": "Công ty Azure Interior",
            "ref": "KH-001",
            "type": "contact",
            "is_company": true,
            "is_customer": true,
            "is_supplier": false,
            "active": true,
            "email": "contact@azure.com",
            "phone": "+84 123 456 789",
            "mobile": "+84 987 654 321",
            "website": "https://azure.com",
            "vat": "0123456789",
            "street": "123 Đường Chính",
            "street2": "Tầng 5",
            "city": "Hồ Chí Minh",
            "zip": "700000",
            "state": {
                "id": 1,
                "name": "Hồ Chí Minh",
                "code": "SG"
            },
            "country": {
                "id": 233,
                "name": "Vietnam",
                "code": "VN"
            },
            "parent": null,
            "company": {
                "id": 1,
                "name": "Công ty của tôi"
            },
            "user": {
                "id": 2,
                "name": "Nhân viên A"
            },
            "comment": "Khách hàng VIP",
            "categories": [
                {
                    "id": 1,
                    "name": "Vàng"
                }
            ],
            "lang": "vi_VN",
            "tz": "Asia/Ho_Chi_Minh",
            "contacts": [
                {
                    "id": 8,
                    "name": "Nguyễn Văn A",
                    "type": "contact",
                    "email": "nva@azure.com",
                    "phone": "+84 123 456 790",
                    "mobile": "+84 987 654 320",
                    "function": "Giám đốc bán hàng"
                }
            ],
            "payment_term": {
                "id": 1,
                "name": "30 Ngày"
            },
            "create_date": "2024-01-01T00:00:00",
            "write_date": "2024-11-25T10:00:00"
        }
    ],
    "pagination": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5,
        "offset": 0,
        "has_next": true,
        "has_previous": false
    },
    "filters_applied": {
        "search": null,
        "type": null,
        "is_company": null,
        "customer": "true",
        "supplier": null,
        "active": "true"
    }
}
```

---

### 4.2. Lấy Chi Tiết Đối Tác

Lấy thông tin chi tiết của một đối tác theo ID.

**Endpoint**: `GET /api/v1/partners/{partner_id}`

**Quyền**: `api_allow_partner`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `partner_id` | integer | Có | ID đối tác |

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `include_contacts` | boolean | Không | true | Bao gồm liên hệ con |
| `include_addresses` | boolean | Không | true | Bao gồm địa chỉ |

#### Ví Dụ Request

```bash
GET /api/v1/partners/7?include_contacts=true&include_addresses=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin đối tác thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 7,
        "name": "Công ty Azure Interior",
        "display_name": "Công ty Azure Interior",
        "ref": "KH-001",
        "type": "contact",
        "is_company": true,
        "is_customer": true,
        "is_supplier": false,
        "active": true,
        "email": "contact@azure.com",
        "phone": "+84 123 456 789",
        "mobile": "+84 987 654 321",
        "website": "https://azure.com",
        "vat": "0123456789",
        "street": "123 Đường Chính",
        "street2": "Tầng 5",
        "city": "Hồ Chí Minh",
        "zip": "700000",
        "state": {
            "id": 1,
            "name": "Hồ Chí Minh",
            "code": "SG"
        },
        "country": {
            "id": 233,
            "name": "Vietnam",
            "code": "VN"
        },
        "parent": null,
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "user": {
            "id": 2,
            "name": "Nhân viên A"
        },
        "comment": "Khách hàng VIP",
        "categories": [
            {
                "id": 1,
                "name": "Vàng"
            }
        ],
        "lang": "vi_VN",
        "tz": "Asia/Ho_Chi_Minh",
        "contacts": [
            {
                "id": 8,
                "name": "Nguyễn Văn A",
                "type": "contact",
                "email": "nva@azure.com",
                "phone": "+84 123 456 790",
                "mobile": "+84 987 654 320",
                "function": "Giám đốc bán hàng"
            },
            {
                "id": 9,
                "name": "Trần Thị B",
                "type": "contact",
                "email": "ttb@azure.com",
                "phone": "+84 123 456 791",
                "mobile": null,
                "function": "Kế toán trưởng"
            }
        ],
        "addresses": {
            "invoice": {
                "id": 10,
                "name": "Địa chỉ xuất hóa đơn",
                "street": "456 Đường Hóa Đơn",
                "street2": null,
                "city": "Hồ Chí Minh",
                "zip": "700001",
                "state": {
                    "id": 1,
                    "name": "Hồ Chí Minh"
                },
                "country": {
                    "id": 233,
                    "name": "Vietnam",
                    "code": "VN"
                },
                "phone": "+84 123 456 792",
                "email": "invoice@azure.com"
            },
            "delivery": {
                "id": 11,
                "name": "Địa chỉ giao hàng",
                "street": "789 Đường Giao Hàng",
                "street2": "Kho A",
                "city": "Hồ Chí Minh",
                "zip": "700002",
                "state": {
                    "id": 1,
                    "name": "Hồ Chí Minh"
                },
                "country": {
                    "id": 233,
                    "name": "Vietnam",
                    "code": "VN"
                },
                "phone": "+84 123 456 793",
                "email": null
            },
            "contact": null,
            "other": null
        },
        "payment_term": {
            "id": 1,
            "name": "30 Ngày"
        },
        "supplier_payment_term": null,
        "create_date": "2024-01-01T00:00:00",
        "write_date": "2024-11-25T10:00:00"
    }
}
```

---

### 4.3. Tạo Đối Tác Mới

Tạo mới một đối tác (khách hàng/nhà cung cấp/liên hệ).

**Endpoint**: `POST /api/v1/partners/create`

**Quyền**: `api_allow_partner_create`

**Content-Type**: `application/json`

#### Query Parameters

Không có query parameters.

#### Request Body

```json
{
    "name": "Tên công ty",
    "ref": "REF001",
    "email": "contact@example.com",
    "phone": "+84 123 456 789",
    "mobile": "+84 987 654 321",
    "website": "https://example.com",
    "vat": "1234567890",
    "is_company": true,
    "type": "contact",
    "street": "123 Đường Chính",
    "street2": "Căn hộ 4B",
    "city": "Hồ Chí Minh",
    "zip": "700000",
    "state_id": 1,
    "country_id": 233,
    "parent_id": null,
    "customer": true,
    "supplier": false,
    "category_ids": [1, 2],
    "user_id": 2,
    "company_id": 1
}
```

**Giải thích các trường:**

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `name` | string | **Có** | Tên đối tác (tối thiểu 2 ký tự) |
| `ref` | string | Không | Mã tham chiếu nội bộ |
| `email` | string | Không | Email (định dạng hợp lệ) |
| `phone` | string | Không | Số điện thoại |
| `mobile` | string | Không | Số di động |
| `website` | string | Không | Website |
| `vat` | string | Không | Mã số thuế |
| `is_company` | boolean | Không | Là công ty (mặc định: false) |
| `type` | string | Không | Loại: contact, invoice, delivery, other, private |
| `street` | string | Không | Địa chỉ dòng 1 |
| `street2` | string | Không | Địa chỉ dòng 2 |
| `city` | string | Không | Thành phố |
| `zip` | string | Không | Mã bưu điện |
| `state_id` | integer | Không | ID tỉnh/thành |
| `country_id` | integer | Không | ID quốc gia |
| `parent_id` | integer | Không | ID đối tác cha |
| `customer` | boolean | Không | Đặt là khách hàng |
| `supplier` | boolean | Không | Đặt là nhà cung cấp |
| `category_ids` | array | Không | Mảng ID nhóm đối tác |
| `user_id` | integer | Không | ID người phụ trách |
| `company_id` | integer | Không | ID công ty |

#### Ví Dụ Request

```bash
POST /api/v1/partners/create
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "name": "Công ty Giải pháp Công nghệ",
    "email": "info@techsolutions.com",
    "phone": "+84 123 456 789",
    "is_company": true,
    "street": "123 Đường Công Nghệ",
    "city": "Hồ Chí Minh",
    "country_id": 233,
    "customer": true,
    "vat": "0123456789"
}
```

#### Ví Dụ Response (Thành công)

```json
{
    "status": "success",
    "message": "Tạo đối tác thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 150,
        "name": "Công ty Giải pháp Công nghệ",
        "display_name": "Công ty Giải pháp Công nghệ",
        "ref": null,
        "type": "contact",
        "is_company": true,
        "is_customer": true,
        "is_supplier": false,
        "active": true,
        "email": "info@techsolutions.com",
        "phone": "+84 123 456 789",
        "mobile": null,
        "website": null,
        "vat": "0123456789",
        "street": "123 Đường Công Nghệ",
        "street2": null,
        "city": "Hồ Chí Minh",
        "zip": null,
        "state": null,
        "country": {
            "id": 233,
            "name": "Vietnam",
            "code": "VN"
        },
        "parent": null,
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "user": null,
        "comment": null,
        "categories": [],
        "lang": "vi_VN",
        "tz": false,
        "create_date": "2024-11-25T10:00:00",
        "write_date": "2024-11-25T10:00:00"
    }
}
```

#### Ví Dụ Response (Lỗi Validation)

```json
{
    "status": "error",
    "message": "Validation thất bại",
    "timestamp": "2024-11-25T10:00:00Z",
    "errors": [
        "name là bắt buộc",
        "định dạng email không hợp lệ",
        "Không tìm thấy quốc gia với ID 999"
    ]
}
```

### 4.4. Cập Nhật Đối Tác

Cập nhật thông tin cơ bản của một đối tác.

**Endpoint**: `PUT /api/v1/partners/{partner_id}/update`

**Quyền**: `api_allow_partner_update`

**Content-Type**: `application/json`

**Lưu ý**: API này chỉ cho phép cập nhật các thông tin liên hệ và địa chỉ cơ bản. Không thể thay đổi type, parent_id, is_company, hoặc các trường quan hệ khác.

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `partner_id` | integer | Có | ID đối tác cần cập nhật |

#### Query Parameters

Không có query parameters.

#### Request Body
```json
{
    "name": "Tên công ty đã cập nhật",
    "email": "newemail@example.com",
    "phone": "+84 123 456 789",
    "mobile": "+84 987 654 321",
    "website": "https://newwebsite.com",
    "vat": "9876543210",
    "street": "456 Đường Mới",
    "street2": "Tầng 10",
    "city": "Hà Nội",
    "zip": "100000",
    "state_id": 2,
    "country_id": 233,
    "lang": "vi_VN",
    "tz": "Asia/Ho_Chi_Minh"
}
```

**Các trường được phép cập nhật:**

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `name` | string | Tên đối tác (tối thiểu 2 ký tự) |
| `email` | string | Email (định dạng hợp lệ) |
| `phone` | string | Số điện thoại |
| `mobile` | string | Số di động |
| `website` | string | Website |
| `vat` | string | Mã số thuế |
| `street` | string | Địa chỉ dòng 1 |
| `street2` | string | Địa chỉ dòng 2 |
| `city` | string | Thành phố |
| `zip` | string | Mã bưu điện |
| `state_id` | integer | ID tỉnh/thành |
| `country_id` | integer | ID quốc gia |
| `lang` | string | Ngôn ngữ (vi_VN, en_US, ...) |
| `tz` | string | Múi giờ (Asia/Ho_Chi_Minh, ...) |

**Lưu ý**: Chỉ cần gửi các trường muốn cập nhật, không cần gửi tất cả.

#### Ví Dụ Request
```bash
PUT /api/v1/partners/150/update
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "name": "Công ty Giải Pháp Công Nghệ ABC",
    "email": "contact@techsolutions.com.vn",
    "phone": "+84 28 1234 5678",
    "street": "456 Đường Lê Lợi",
    "city": "Hồ Chí Minh",
    "state_id": 1
}
```

#### Ví Dụ Response (Thành công)
```json
{
    "status": "success",
    "message": "Cập nhật đối tác thành công",
    "version": "v1",
    "timestamp": "2024-12-19T10:00:00Z",
    "data": {
        "id": 150,
        "name": "Công ty Giải Pháp Công Nghệ ABC",
        "display_name": "Công ty Giải Pháp Công Nghệ ABC",
        "ref": null,
        "type": "contact",
        "is_company": true,
        "is_customer": true,
        "is_supplier": false,
        "active": true,
        "email": "contact@techsolutions.com.vn",
        "phone": "+84 28 1234 5678",
        "mobile": null,
        "website": null,
        "vat": "0123456789",
        "street": "456 Đường Lê Lợi",
        "street2": null,
        "city": "Hồ Chí Minh",
        "zip": null,
        "state": {
            "id": 1,
            "name": "Hồ Chí Minh",
            "code": "SG"
        },
        "country": {
            "id": 233,
            "name": "Vietnam",
            "code": "VN"
        },
        "parent": null,
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "user": null,
        "comment": null,
        "categories": [],
        "lang": "vi_VN",
        "tz": "Asia/Ho_Chi_Minh",
        "create_date": "2024-11-25T10:00:00",
        "write_date": "2024-12-19T10:00:00"
    },
    "updated_fields": [
        "name",
        "email",
        "phone",
        "street",
        "city",
        "state_id"
    ]
}
```

#### Ví Dụ Response (Lỗi Validation)
```json
{
    "status": "error",
    "message": "Validation thất bại",
    "timestamp": "2024-12-19T10:00:00Z",
    "errors": [
        "định dạng email không hợp lệ",
        "Không tìm thấy quốc gia với ID 999",
        "Các trường không được phép cập nhật: is_company, ref"
    ]
}
```

---

### 4.5. Xóa Đối Tác (Vô Hiệu Hóa)

Xóa (vô hiệu hóa) một đối tác bằng cách đặt `active = False`.

**Endpoint**: `DELETE /api/v1/partners/{partner_id}/delete`

**Quyền**: `api_allow_partner_delete`

**Lưu ý**: 
- Đây là soft delete, không xóa thật khỏi database
- Tự động vô hiệu hóa tất cả đối tác con (children)
- Không thể xóa đối tác hệ thống (ID 1-6)
- Không thể xóa đối tác đã bị vô hiệu hóa

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `partner_id` | integer | Có | ID đối tác cần xóa |

#### Query Parameters

Không có query parameters.

#### Request Body

Không có request body.

#### Ví Dụ Request
```bash
DELETE /api/v1/partners/150/delete
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response (Thành công)
```json
{
    "status": "success",
    "message": "Vô hiệu hóa đối tác thành công",
    "version": "v1",
    "timestamp": "2024-12-19T10:00:00Z",
    "data": {
        "partner_id": 150,
        "partner_name": "Công ty Giải Pháp Công Nghệ ABC",
        "partner_type": "contact",
        "deactivated_count": 4,
        "children_count": 3,
        "deactivated_records": [
            {
                "id": 150,
                "name": "Công ty Giải Pháp Công Nghệ ABC",
                "type": "contact",
                "is_main": true
            },
            {
                "id": 151,
                "name": "Địa chỉ giao hàng",
                "type": "delivery",
                "is_main": false
            },
            {
                "id": 152,
                "name": "Địa chỉ xuất hóa đơn",
                "type": "invoice",
                "is_main": false
            },
            {
                "id": 153,
                "name": "Nguyễn Văn A - Liên hệ",
                "type": "contact",
                "is_main": false
            }
        ]
    }
}
```

#### Ví Dụ Response (Lỗi)
```json
{
    "status": "error",
    "message": "Đối tác với ID 150 đã bị vô hiệu hóa",
    "timestamp": "2024-12-19T10:00:00Z"
}
```
```json
{
    "status": "error",
    "message": "Không thể xóa đối tác hệ thống (ID 1)",
    "timestamp": "2024-12-19T10:00:00Z"
}
```


---

## 5. API ĐƠN HÀNG BÁN

### 5.1. Lấy Danh Sách Đơn Hàng

Lấy danh sách các đơn hàng bán.

**Endpoint**: `GET /api/v1/sale-orders`

**Quyền**: `api_allow_sale_order`

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `page` | integer | Không | 1 | Số trang |
| `page_size` | integer | Không | 20 | Số bản ghi mỗi trang (tối đa: 100) |
| `limit` | integer | Không | 20 | Thay thế cho page_size |
| `offset` | integer | Không | 0 | Bỏ qua N bản ghi |
| `sort` | string | Không | date_order | Trường sắp xếp |
| `order` | string | Không | desc | Thứ tự sắp xếp |
| `search` | string | Không | - | Tìm trong tên đơn hàng |
| `state` | string | Không | - | Trạng thái: `draft`, `sent`, `sale`, `done`, `cancel` (ngăn cách bằng dấu phẩy) |
| `partner_id` | integer | Không | - | ID khách hàng |
| `partner_name` | string | Không | - | Tên khách hàng (tìm gần đúng) |
| `date_from` | string | Không | - | Từ ngày (YYYY-MM-DD) |
| `date_to` | string | Không | - | Đến ngày (YYYY-MM-DD) |
| `amount_min` | float | Không | - | Tổng tiền tối thiểu |
| `amount_max` | float | Không | - | Tổng tiền tối đa |
| `company_id` | integer | Không | - | ID công ty |
| `include_lines` | boolean | Không | false | Bao gồm chi tiết đơn hàng |

#### Ví Dụ Request

```bash
GET /api/v1/sale-orders?state=sale,done&date_from=2024-01-01&include_lines=true&page=1
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Tìm thấy 50 đơn hàng",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": [
        {
            "id": 1,
            "name": "SO001",
            "state": "sale",
            "state_display": "Đơn hàng bán",
            "date_order": "2024-11-25T10:00:00",
            "validity_date": "2024-12-25T10:00:00",
            "partner": {
                "id": 7,
                "name": "Công ty Azure Interior",
                "email": "contact@azure.com",
                "phone": "+84 123 456 789",
                "vat": "0123456789",
                "street": "123 Đường Chính",
                "street2": "Tầng 5",
                "city": "Hồ Chí Minh",
                "state": "Hồ Chí Minh",
                "country": "Vietnam"
            },
            "partner_invoice": {
                "id": 8,
                "name": "Azure Interior - Địa chỉ xuất hóa đơn",
                "email": "invoice@azure.com",
                "phone": "+84 123 456 792",
                "vat": "0123456789",
                "street": "456 Đường Hóa Đơn",
                "street2": null,
                "city": "Hồ Chí Minh",
                "state": "Hồ Chí Minh",
                "country": "Vietnam"
            },
            "partner_shipping": {
                "id": 9,
                "name": "Azure Interior - Địa chỉ giao hàng",
                "email": null,
                "phone": "+84 123 456 793",
                "vat": null,
                "street": "789 Đường Giao Hàng",
                "street2": "Kho A",
                "city": "Hồ Chí Minh",
                "state": "Hồ Chí Minh",
                "country": "Vietnam"
            },
            "company": {
                "id": 1,
                "name": "Công ty của tôi"
            },
            "currency": {
                "id": 1,
                "name": "USD",
                "symbol": "$"
            },
            "amount_untaxed": 1000.00,
            "amount_tax": 100.00,
            "amount_total": 1100.00,
            "note": "Ghi chú giao hàng đặc biệt",
            "payment_term": {
                "id": 1,
                "name": "30 Ngày"
            },
            "order_lines": [
                {
                    "id": 1,
                    "product": {
                        "id": 1,
                        "name": "Laptop Dell XPS 13",
                        "default_code": "LAPTOP-001"
                    },
                    "name": "Laptop Dell XPS 13",
                    "product_uom_qty": 2.0,
                    "product_uom": {
                        "id": 1,
                        "name": "Cái"
                    },
                    "price_unit": 500.00,
                    "discount": 0.0,
                    "tax_ids": [
                        {
                            "id": 1,
                            "name": "VAT 10%",
                            "amount": 10.0
                        }
                    ],
                    "price_subtotal": 1000.00,
                    "price_total": 1100.00
                }
            ],
            "create_date": "2024-11-25T10:00:00",
            "write_date": "2024-11-25T10:00:00"
        }
    ],
    "pagination": {
        "total": 50,
        "page": 1,
        "page_size": 20,
        "total_pages": 3,
        "offset": 0,
        "has_next": true,
        "has_previous": false
    },
    "filters_applied": {
        "search": null,
        "state": "sale,done",
        "partner_name": null,
        "date_from": "2024-01-01",
        "date_to": null
    }
}
```

---

### 5.2. Lấy Chi Tiết Đơn Hàng

Lấy thông tin chi tiết của một đơn hàng theo ID.

**Endpoint**: `GET /api/v1/sale-orders/{order_id}`

**Quyền**: `api_allow_sale_order`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `order_id` | integer | Có | ID đơn hàng |

#### Query Parameters

| Tham số | Kiểu | Bắt buộc | Mặc định | Mô tả |
|---------|------|----------|----------|-------|
| `include_lines` | boolean | Không | true | Bao gồm chi tiết đơn hàng |

#### Ví Dụ Request

```bash
GET /api/v1/sale-orders/1?include_lines=true
Authorization: Bearer YOUR_TOKEN
```

#### Ví Dụ Response

```json
{
    "status": "success",
    "message": "Lấy thông tin đơn hàng thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 1,
        "name": "SO001",
        "state": "sale",
        "state_display": "Đơn hàng bán",
        "date_order": "2024-11-25T10:00:00",
        "validity_date": "2024-12-25T10:00:00",
        "partner": {
            "id": 7,
            "name": "Công ty Azure Interior",
            "email": "contact@azure.com",
            "phone": "+84 123 456 789",
            "vat": "0123456789",
            "street": "123 Đường Chính",
            "street2": "Tầng 5",
            "city": "Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "country": "Vietnam"
        },
        "partner_invoice": {
            "id": 8,
            "name": "Azure Interior - Địa chỉ xuất hóa đơn",
            "email": "invoice@azure.com",
            "phone": "+84 123 456 792",
            "vat": "0123456789",
            "street": "456 Đường Hóa Đơn",
            "street2": null,
            "city": "Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "country": "Vietnam"
        },
        "partner_shipping": {
            "id": 9,
            "name": "Azure Interior - Địa chỉ giao hàng",
            "email": null,
            "phone": "+84 123 456 793",
            "vat": null,
            "street": "789 Đường Giao Hàng",
            "street2": "Kho A",
            "city": "Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "country": "Vietnam"
        },
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "currency": {
            "id": 1,
            "name": "USD",
            "symbol": "$"
        },
        "amount_untaxed": 1000.00,
        "amount_tax": 100.00,
        "amount_total": 1100.00,
        "note": "Ghi chú giao hàng đặc biệt",
        "payment_term": {
            "id": 1,
            "name": "30 Ngày"
        },
        "order_lines": [
            {
                "id": 1,
                "product": {
                    "id": 1,
                    "name": "Laptop Dell XPS 13",
                    "default_code": "LAPTOP-001"
                },
                "name": "Laptop Dell XPS 13",
                "product_uom_qty": 2.0,
                "product_uom": {
                    "id": 1,
                    "name": "Cái"
                },
                "price_unit": 500.00,
                "discount": 0.0,
                "tax_ids": [
                    {
                        "id": 1,
                        "name": "VAT 10%",
                        "amount": 10.0
                    }
                ],
                "price_subtotal": 1000.00,
                "price_total": 1100.00
            }
        ],
        "create_date": "2024-11-25T09:30:00",
        "write_date": "2024-11-25T10:00:00"
    }
}
```

---

### 5.3. Tạo Đơn Hàng Mới

Tạo một đơn hàng bán mới.

**Endpoint**: `POST /api/v1/sale-orders/create`

**Quyền**: `api_allow_sale_order_create`

**Content-Type**: `application/json`

#### Query Parameters

Không có query parameters.

#### Request Body

```json
{
    "partner_id": 123,
    "date_order": "2024-11-25T10:00:00",
    "client_order_ref": "PO-2024-001",
    "user_id": 2,
    "payment_term_id": 1,
    "company_id": 1,
    "note": "Giao hàng trước 5h chiều",
    "order_lines": [
        {
            "product_id": 456,
            "product_uom_qty": 2,
            "price_unit": 100.00,
            "discount": 10,
            "name": "Mô tả tùy chỉnh",
            "product_uom": 1,
            "tax_ids": [1, 2]
        }
    ],
    "confirm_order": true
}
```

**Giải thích các trường:**

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `partner_id` | integer | **Có** | ID khách hàng |
| `date_order` | string | Không | Ngày đặt hàng (ISO format) |
| `client_order_ref` | string | Không | Mã đơn hàng khách |
| `user_id` | integer | Không | ID nhân viên bán hàng |
| `payment_term_id` | integer | Không | ID điều khoản thanh toán |
| `company_id` | integer | Không | ID công ty |
| `note` | string | Không | Ghi chú nội bộ |
| `order_lines` | array | **Có** | Mảng chi tiết đơn hàng (tối thiểu 1 dòng) |
| `confirm_order` | boolean | Không | Tự động xác nhận (mặc định: false) |

**Chi tiết order_lines:**

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `product_id` | integer | **Có** | ID sản phẩm |
| `product_uom_qty` | float | **Có** | Số lượng (phải > 0) |
| `price_unit` | float | Không | Đơn giá (dùng giá sản phẩm nếu không có) |
| `discount` | float | Không | Chiết khấu % (0-100) |
| `name` | string | Không | Mô tả dòng |
| `product_uom` | integer | Không | ID đơn vị tính |
| `tax_ids` | array | Không | Mảng ID thuế |

#### Ví Dụ Request

```bash
POST /api/v1/sale-orders/create
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "partner_id": 7,
    "client_order_ref": "PO-2024-100",
    "order_lines": [
        {
            "product_id": 1,
            "product_uom_qty": 2,
            "price_unit": 500.00,
            "discount": 5
        },
        {
            "product_id": 2,
            "product_uom_qty": 1,
            "price_unit": 200.00
        }
    ],
    "confirm_order": false
}
```

#### Ví Dụ Response (Thành công)

```json
{
    "status": "success",
    "message": "Tạo đơn hàng thành công",
    "version": "v1",
    "timestamp": "2024-11-25T10:00:00Z",
    "data": {
        "id": 51,
        "name": "SO051",
        "state": "draft",
        "state_display": "Báo giá",
        "date_order": "2024-11-25T10:00:00",
        "validity_date": null,
        "partner": {
            "id": 7,
            "name": "Công ty Azure Interior",
            "email": "contact@azure.com",
            "phone": "+84 123 456 789",
            "vat": "0123456789",
            "street": "123 Đường Chính",
            "street2": "Tầng 5",
            "city": "Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "country": "Vietnam"
        },
        "partner_invoice": {
            "id": 7,
            "name": "Công ty Azure Interior",
            "email": "contact@azure.com",
            "phone": "+84 123 456 789",
            "vat": "0123456789",
            "street": "123 Đường Chính",
            "street2": "Tầng 5",
            "city": "Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "country": "Vietnam"
        },
        "partner_shipping": {
            "id": 7,
            "name": "Công ty Azure Interior",
            "email": "contact@azure.com",
            "phone": "+84 123 456 789",
            "vat": "0123456789",
            "street": "123 Đường Chính",
            "street2": "Tầng 5",
            "city": "Hồ Chí Minh",
            "state": "Hồ Chí Minh",
            "country": "Vietnam"
        },
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "currency": {
            "id": 1,
            "name": "USD",
            "symbol": "$"
        },
        "amount_untaxed": 1150.00,
        "amount_tax": 115.00,
        "amount_total": 1265.00,
        "note": null,
        "payment_term": null,
        "order_lines": [
            {
                "id": 101,
                "product": {
                    "id": 1,
                    "name": "Laptop Dell XPS 13",
                    "default_code": "LAPTOP-001"
                },
                "name": "Laptop Dell XPS 13",
                "product_uom_qty": 2.0,
                "product_uom": {
                    "id": 1,
                    "name": "Cái"
                },
                "price_unit": 500.00,
                "discount": 5.0,
                "tax_ids": [
                    {
                        "id": 1,
                        "name": "VAT 10%",
                        "amount": 10.0
                    }
                ],
                "price_subtotal": 950.00,
                "price_total": 1045.00
            },
            {
                "id": 102,
                "product": {
                    "id": 2,
                    "name": "Chuột Logitech",
                    "default_code": "MOUSE-001"
                },
                "name": "Chuột Logitech",
                "product_uom_qty": 1.0,
                "product_uom": {
                    "id": 1,
                    "name": "Cái"
                },
                "price_unit": 200.00,
                "discount": 0.0,
                "tax_ids": [
                    {
                        "id": 1,
                        "name": "VAT 10%",
                        "amount": 10.0
                    }
                ],
                "price_subtotal": 200.00,
                "price_total": 220.00
            }
        ],
        "create_date": "2024-11-25T10:00:00",
        "write_date": "2024-11-25T10:00:00"
    }
}
```

#### Ví Dụ Response (Lỗi Validation)

```json
{
    "status": "error",
    "message": "Validation thất bại",
    "timestamp": "2024-11-25T10:00:00Z",
    "errors": [
        "partner_id là bắt buộc",
        "Dòng 1: product_id là bắt buộc",
        "Dòng 2: product_uom_qty phải lớn hơn 0",
        "Dòng 3: Sản phẩm Test (ID: 999) không thể bán"
    ]
}
```

### 5.4. Cập Nhật Đơn Hàng

Cập nhật thông tin đơn hàng khi ở trạng thái `draft` hoặc `sent`.

**Endpoint**: `PUT /api/v1/sale-orders/{order_id}/update`

**Quyền**: `api_allow_sale_order_update`

**Content-Type**: `application/json`

**Lưu ý**: 
- Chỉ có thể cập nhật đơn hàng ở trạng thái `draft` hoặc `sent`
- Có thể thay đổi khách hàng, thêm/sửa/xóa chi tiết đơn hàng
- Hỗ trợ cả PUT và PATCH methods

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `order_id` | integer | Có | ID đơn hàng cần cập nhật |

#### Query Parameters

Không có query parameters.

#### Request Body
```json
{
    "partner_id": 456,
    "client_order_ref": "PO-2024-002",
    "user_id": 3,
    "payment_term_id": 2,
    "note": "Cập nhật ghi chú giao hàng",
    "order_lines": [
        {
            "action": "create",
            "product_id": 10,
            "product_uom_qty": 5,
            "price_unit": 100.00,
            "discount": 10,
            "name": "Mô tả tùy chỉnh",
            "product_uom": 1,
            "tax_ids": [1]
        },
        {
            "action": "update",
            "line_id": 456,
            "product_uom_qty": 3,
            "price_unit": 150.00,
            "discount": 5
        },
        {
            "action": "delete",
            "line_id": 789
        }
    ]
}
```

**Các trường được phép cập nhật:**

| Trường | Kiểu | Mô tả |
|--------|------|-------|
| `partner_id` | integer | ID khách hàng mới |
| `client_order_ref` | string | Mã đơn hàng khách |
| `user_id` | integer | ID nhân viên bán hàng |
| `payment_term_id` | integer | ID điều khoản thanh toán |
| `note` | string | Ghi chú nội bộ |
| `order_lines` | array | Mảng thao tác trên chi tiết đơn hàng |

**Chi tiết order_lines actions:**

**Action: create** (Tạo dòng mới)

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `action` | string | Có | Giá trị: "create" |
| `product_id` | integer | Có | ID sản phẩm |
| `product_uom_qty` | float | Có | Số lượng (> 0) |
| `price_unit` | float | Không | Đơn giá |
| `discount` | float | Không | Chiết khấu % (0-100) |
| `name` | string | Không | Mô tả dòng |
| `product_uom` | integer | Không | ID đơn vị tính |
| `tax_ids` | array | Không | Mảng ID thuế |

**Action: update** (Cập nhật dòng hiện có)

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `action` | string | Có | Giá trị: "update" |
| `line_id` | integer | Có | ID dòng cần cập nhật |
| `product_id` | integer | Không | ID sản phẩm mới |
| `product_uom_qty` | float | Không | Số lượng mới |
| `price_unit` | float | Không | Đơn giá mới |
| `discount` | float | Không | Chiết khấu mới |
| `name` | string | Không | Mô tả mới |
| `product_uom` | integer | Không | ID đơn vị tính mới |
| `tax_ids` | array | Không | Mảng ID thuế mới |

**Action: delete** (Xóa dòng)

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `action` | string | Có | Giá trị: "delete" |
| `line_id` | integer | Có | ID dòng cần xóa |

**Lưu ý**: Chỉ cần gửi các trường muốn cập nhật.

#### Ví Dụ Request (Cập nhật khách hàng)
```bash
PUT /api/v1/sale-orders/51/update
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "partner_id": 7,
    "client_order_ref": "PO-2024-100-V2",
    "note": "Khách yêu cầu giao trước 5h"
}
```

#### Ví Dụ Request (Thêm và xóa order lines)
```bash
PATCH /api/v1/sale-orders/51/update
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "order_lines": [
        {
            "action": "create",
            "product_id": 3,
            "product_uom_qty": 10,
            "price_unit": 50.00
        },
        {
            "action": "update",
            "line_id": 101,
            "product_uom_qty": 5,
            "discount": 15
        },
        {
            "action": "delete",
            "line_id": 102
        }
    ]
}
```

#### Ví Dụ Response (Thành công)
```json
{
    "status": "success",
    "message": "Cập nhật đơn hàng thành công",
    "version": "v1",
    "timestamp": "2024-12-19T10:00:00Z",
    "data": {
        "id": 51,
        "name": "SO051",
        "state": "draft",
        "state_display": "Báo giá",
        "date_order": "2024-11-25T10:00:00",
        "validity_date": null,
        "partner": {
            "id": 7,
            "name": "Công ty Azure Interior",
            "email": "contact@azure.com",
            "phone": "+84 123 456 789"
        },
        "company": {
            "id": 1,
            "name": "Công ty của tôi"
        },
        "currency": {
            "id": 1,
            "name": "USD",
            "symbol": "$"
        },
        "amount_untaxed": 950.00,
        "amount_tax": 95.00,
        "amount_total": 1045.00,
        "note": "Khách yêu cầu giao trước 5h",
        "order_lines": [
            {
                "id": 101,
                "product": {
                    "id": 1,
                    "name": "Laptop Dell XPS 13",
                    "default_code": "LAPTOP-001"
                },
                "name": "Laptop Dell XPS 13",
                "product_uom_qty": 5.0,
                "price_unit": 500.00,
                "discount": 15.0,
                "price_subtotal": 2125.00,
                "price_total": 2337.50
            },
            {
                "id": 103,
                "product": {
                    "id": 3,
                    "name": "Bàn phím Logitech",
                    "default_code": "KEY-001"
                },
                "name": "Bàn phím Logitech",
                "product_uom_qty": 10.0,
                "price_unit": 50.00,
                "discount": 0.0,
                "price_subtotal": 500.00,
                "price_total": 550.00
            }
        ],
        "create_date": "2024-11-25T10:00:00",
        "write_date": "2024-12-19T10:00:00"
    },
    "updated_fields": [
        "partner_id",
        "client_order_ref",
        "note"
    ],
    "changes": {
        "order_lines": {
            "created": [
                {
                    "id": 103,
                    "product": "Bàn phím Logitech",
                    "quantity": 10.0
                }
            ],
            "updated": [
                {
                    "id": 101,
                    "product": "Laptop Dell XPS 13",
                    "updated_fields": [
                        "product_uom_qty",
                        "discount"
                    ]
                }
            ],
            "deleted": [
                {
                    "id": 102,
                    "product": "Chuột Logitech",
                    "quantity": 1.0
                }
            ]
        }
    }
}
```

#### Ví Dụ Response (Lỗi Validation)
```json
{
    "status": "error",
    "message": "Validation thất bại",
    "timestamp": "2024-12-19T10:00:00Z",
    "errors": [
        "Không thể cập nhật đơn hàng ở trạng thái 'sale'. Chỉ có thể cập nhật 'draft' hoặc 'sent'",
        "Dòng 1 (update): ID dòng 456 không tìm thấy",
        "Dòng 2 (create): product_uom_qty phải lớn hơn 0",
        "Dòng 3 (delete): Dòng 789 không thuộc đơn hàng này"
    ]
}
```

---

### 5.5. Thay Đổi Trạng Thái Đơn Hàng

Thay đổi trạng thái của đơn hàng (xác nhận, hủy, gửi quotation, đưa về draft).

**Endpoint**: `POST /api/v1/sale-orders/{order_id}/change-state`

**Quyền**: `api_allow_sale_order_change_state`

**Content-Type**: `application/json`

#### URL Parameters

| Tham số | Kiểu | Bắt buộc | Mô tả |
|---------|------|----------|-------|
| `order_id` | integer | Có | ID đơn hàng cần thay đổi trạng thái |

#### Query Parameters

Không có query parameters.

#### Request Body
```json
{
    "action": "confirm",
    "reason": "Lý do hủy đơn (bắt buộc khi action = cancel)"
}
```

**Các action được hỗ trợ:**

| Action | Từ Trạng Thái | Đến Trạng Thái | Mô Tả |
|--------|---------------|----------------|-------|
| `confirm` | draft, sent | sale | Xác nhận đơn hàng |
| `cancel` | bất kỳ | cancel | Hủy đơn hàng |
| `draft` | cancel | draft | Đưa về draft |
| `send` | draft | sent | Gửi quotation |

**Tham số:**

| Trường | Kiểu | Bắt buộc | Mô tả |
|--------|------|----------|-------|
| `action` | string | Có | Hành động: confirm, cancel, draft, send |
| `reason` | string | Có (khi action=cancel) | Lý do hủy đơn |

#### Ví Dụ Request (Xác nhận đơn hàng)
```bash
POST /api/v1/sale-orders/51/change-state
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "action": "confirm"
}
```

#### Ví Dụ Request (Hủy đơn hàng)
```bash
POST /api/v1/sale-orders/51/change-state
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "action": "cancel",
    "reason": "Khách hàng yêu cầu hủy do thay đổi kế hoạch"
}
```

#### Ví Dụ Request (Gửi quotation)
```bash
POST /api/v1/sale-orders/51/change-state
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "action": "send"
}
```

#### Ví Dụ Request (Đưa về draft)
```bash
POST /api/v1/sale-orders/51/change-state
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
    "action": "draft"
}
```

#### Ví Dụ Response (Thành công - Confirm)
```json
{
    "status": "success",
    "message": "Xác nhận đơn hàng thành công (đã chuyển từ Báo giá sang Đơn hàng bán)",
    "version": "v1",
    "timestamp": "2024-12-19T10:00:00Z",
    "data": {
        "id": 51,
        "name": "SO051",
        "state": "sale",
        "state_display": "Đơn hàng bán",
        "previous_state": "draft",
        "previous_state_display": "Báo giá",
        "action": "confirm",
        "partner": {
            "id": 7,
            "name": "Công ty Azure Interior"
        },
        "amount_total": 1045.00
    }
}
```

#### Ví Dụ Response (Thành công - Cancel)
```json
{
    "status": "success",
    "message": "Hủy đơn hàng thành công. Lý do: Khách hàng yêu cầu hủy do thay đổi kế hoạch",
    "version": "v1",
    "timestamp": "2024-12-19T10:00:00Z",
    "data": {
        "id": 51,
        "name": "SO051",
        "state": "cancel",
        "state_display": "Đã hủy",
        "previous_state": "draft",
        "previous_state_display": "Báo giá",
        "action": "cancel",
        "partner": {
            "id": 7,
            "name": "Công ty Azure Interior"
        },
        "amount_total": 1045.00
    }
}
```

#### Ví Dụ Response (Lỗi)
```json
{
    "status": "error",
    "message": "Không thể xác nhận đơn hàng ở trạng thái 'cancel'. Chỉ có thể xác nhận 'draft' hoặc 'sent'",
    "timestamp": "2024-12-19T10:00:00Z"
}
```
```json
{
    "status": "error",
    "message": "Không thể xác nhận đơn hàng không có chi tiết đơn hàng",
    "timestamp": "2024-12-19T10:00:00Z"
}
```
```json
{
    "status": "error",
    "message": "Đơn hàng đã bị hủy",
    "timestamp": "2024-12-19T10:00:00Z"
}
```
```json
{
    "status": "error",
    "message": "Action không hợp lệ. Phải là một trong: confirm, cancel, draft, send",
    "timestamp": "2024-12-19T10:00:00Z"
}
```

---

## PHỤ LỤC

### A. Phân Trang

Tất cả endpoint danh sách đều hỗ trợ phân trang:

**Cách 1: Dùng page và page_size**
```
?page=1&page_size=20
```

**Cách 2: Dùng limit và offset**
```
?limit=20&offset=40
```

### B. Sắp Xếp

```
?sort=name&order=asc          # Sắp xếp theo tên, tăng dần
?sort=create_date&order=desc  # Sắp xếp theo ngày tạo, giảm dần
```

### C. Lọc

**Nhiều giá trị (ngăn cách bằng dấu phẩy):**
```
?state=draft,sale,done
?type=product,service
```

**Lọc boolean:**
```
?active=true
?customer=true
?include_stock=false
```

**Lọc khoảng ngày:**
```
?date_from=2024-01-01&date_to=2024-12-31
```

**Lọc khoảng số:**
```
?amount_min=100&amount_max=1000
?price_min=50.00&price_max=500.00
```

### D. Xử Lý Lỗi

**Response lỗi chuẩn:**

```json
{
    "status": "error",
    "message": "Mô tả lỗi",
    "timestamp": "2024-11-25T10:00:00Z",
    "errors": []
}
```

**Các loại lỗi:**

- **400 Bad Request**: Lỗi validation, dữ liệu không hợp lệ
- **401 Unauthorized**: Token không hợp lệ hoặc hết hạn
- **403 Forbidden**: Không có quyền truy cập endpoint
- **404 Not Found**: Không tìm thấy resource theo ID
- **500 Internal Server Error**: Lỗi máy chủ

### E. Ghi Log Giao Dịch

Tất cả lời gọi API được tự động ghi log với:
- Endpoint được truy cập
- User thực hiện request
- Trạng thái và dữ liệu response
- Thời gian thực thi
- Thông báo lỗi (nếu có)

---

## THỰC HÀNH TỐT

1. **Sử dụng phân trang**: Luôn dùng phân trang cho endpoint danh sách để tránh quá tải
2. **Lọc dữ liệu**: Dùng filter cụ thể để giảm kích thước response
3. **Tham số Include**: Chỉ yêu cầu dữ liệu bổ sung khi thực sự cần (`include_*`)
4. **Xử lý lỗi**: Luôn kiểm tra trường `status` trong response
5. **Rate Limiting**: Cài đặt giới hạn tốc độ phù hợp ở phía client
6. **Bảo mật Token**: Lưu token an toàn, không để lộ ở client-side
7. **Validation**: Validate dữ liệu ở phía client trước khi gửi lên server
8. **Idempotency**: Với create operation, cân nhắc dùng idempotency key

---

**Phiên bản**: v1  
**Cập nhật**: 2024-11-25  
**Liên hệ hỗ trợ**: support@your-company.com