# 🔗 Amoeba Talk Connector

[![License: LGPL-3.0](https://img.shields.io/badge/License-LGPL%203.0-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo](https://img.shields.io/badge/Odoo-18.0%20|%2019.0-00A09D.svg)](https://www.odoo.com)

Official Odoo connector for **Amoeba Talk** platform.

---

## 📖 What is this?

This module enables **Amoeba Talk** to connect and sync data with your Odoo system through REST APIs.

**Amoeba Talk can access:**
- 👥 Customers & Suppliers (Partners)
- 📦 Products with stock info
- 🛒 Sale Orders
- 🌍 Countries & States
- 💰 Taxes

---

## 📥 Installation
```bash
# Clone to Odoo addons folder
cd /path/to/odoo/addons
git clone https://github.com/amoeba-group/amoeba-talk-odoo.git amb_talk

# Restart Odoo
# Apps → Update Apps List → Install "Amoeba Talk Connector"
```

---

## ⚙️ Configuration

### 1️⃣ Generate API Token

1. **Settings → Users**
2. Select user **"User Amoeba Talk Connector"**
3. Tab **API Settings** → Click **"Generate API Key"**
4. Copy token (you'll need this for Amoeba Talk)

### 2️⃣ Set Domain Whitelist

Add Amoeba Talk domains:
```
talk.amoeba.group
*.amoeba.group
```

### 3️⃣ Enable Permissions

Check what data Amoeba Talk can access:
- ☑️ Partners
- ☑️ Products  
- ☑️ Sale Orders
- ☑️ Countries/States
- ☑️ Taxes

### 4️⃣ Connect from Amoeba Talk

In **Amoeba Talk dashboard**:
1. Go to **Settings → Integrations → Odoo**
2. Enter Odoo URL: `https://your-odoo.com`
3. Enter API Token from step 1
4. Click **Connect**

---

## 🔌 API Endpoints

All endpoints: `Authorization: Bearer YOUR_TOKEN`

### 🔐 Authentication
```bash
GET /api/v1/auth/check
GET /api/v1/auth/user-info
```

### 👥 Partners
```bash
GET  /api/v1/partners
GET  /api/v1/partners/{id}
POST /api/v1/partners/create
```

### 📦 Products
```bash
GET /api/v1/products
GET /api/v1/products/{id}
```

### 🛒 Sale Orders
```bash
GET  /api/v1/sale-orders
GET  /api/v1/sale-orders/{id}
POST /api/v1/sale-orders/create
```

### 📋 Master Data
```bash
GET /api/v1/countries
GET /api/v1/states
GET /api/v1/taxes
```

---

## 📊 Monitoring

View sync logs: **Settings → Technical → API Transaction Logs**

---

## 🆘 Support

**Module Issues**: [GitHub Issues](https://github.com/amoeba-group/amoeba-talk-odoo/issues)  
**Amoeba Talk Support**: support@amoeba.group  
**Email**: contact@amoeba.group

---

## 📄 License

LGPL-3.0

---

**Made with ❤️ by Amoeba Group**