Merchant X Consumer — 多商家 & 會員後端系統 API

本專案是一個以 Django 5 + Django REST Framework 建構的
多商家（Marketplace）＋ 會員系統（Member System）
後端 API。

支援：

會員註冊 / 登入 / 個資管理

商家申請 / 商店建立

商品管理（商品 CRUD、權限保護、店家綁定）

訂單系統（會員下單、商家查看、自動關聯商品）

角色權限控管（Admin / Merchant / Member）

Owner-Based Permission（只能操作自己的資料）

Token 驗證（可改 JWT）

適用於：

電商平台

多商家上架商品的 marketplace

學習後端架構專案

接案作品集

📁 專案目錄結構
Merchant_X_Consumer/
│
├── config/                  # Django 專案設定
│
├── member/                  # 會員模型與 API
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│
├── merchant/                # 商家模型與 API
│
├── store/                   # 商店與商品管理
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│
├── order/                   # 訂單管理
│
├── requirements.txt         # 套件列表（建議加入）
└── README.md
🔐 使用者角色說明
角色	能力
| 角色                | 能力                  |
| --------------------| ------------------------------------|
| **Admin**           | 管理所有資料、查看全部會員、商家、訂單 |
| **Merchant（商家）** | 建立商店、管理商店資訊、管理自己的商品 |
| **Member（會員）**   | 註冊、登入、編輯個資、購買商品        |
| **訪客**             | 只能瀏覽公開商品與商店               |

🧩 資料庫 ERD

以下是目前模型結構：
User (Django auth user)
│
├── Member (OneToOne)
│     - member_name
│     - member_email
│     - login_days
│     - member_points
│
└── Merchant (OneToOne)
      │
      └── Store (OneToOne)
            │
            └── Product (Many)
                    │
                    └── OrderItem (Many)
                           │
                           └── Order (Many-to-Many through OrderItem)
🔧 安裝方式
git clone https://github.com/iPhonewoo/MerchantMember_ComsumerMember.git
cd MerchantMember_ComsumerMember/Merchant_X_Consumer

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Windows 使用 venv\Scripts\activate

# 安裝套件
pip install -r requirements.txt
pip freeze > requirements.txt

# 建立資料庫
python manage.py migrate

# 啟動伺服器
python manage.py runserver
📘 API 文件
🔑 Auth
| Method | Endpoint         | 說明         |
| ------ | ---------------- | ---------- |
| POST   | `/api/register/` | 註冊         |
| POST   | `/api/login/`    | 登入取得 Token |
👤 Member API
| Method | Endpoint             | 說明             |
| ------ | -------------------- | -------------- |
| GET    | `/api/members/{id}/` | 查看自己的會員資料（需登入） |
| PATCH  | `/api/members/{id}/` | 更新自己的資料        |
| PUT    | `/api/members/{id}/` | 完整更新資料         |
🔒 權限：

只能查看自己的資料（OwnerOnly）

不可查看其他會員（避免個資外洩）

不可用 ViewSet 建立 Member（註冊 API 已處理）

🏬 Store（商店）
| Method | Endpoint            | 說明              |
| ------ | ------------------- | --------------- |
| POST   | `/api/stores/`      | 商家建立商店（每商家只能一間） |
| GET    | `/api/stores/`      | 查看所有商店          |
| GET    | `/api/stores/{id}/` | 查看單一商店          |
| PATCH  | `/api/stores/{id}/` | 商家修改自己的商店       |
| DELETE | `/api/stores/{id}/` | 刪除（限 owner）     |
📦 Product（商品）
| Method | Endpoint              | 說明     |
| ------ | --------------------- | ------ |
| POST   | `/api/products/`      | 商家新增商品 |
| GET    | `/api/products/`      | 查看商品列表 |
| GET    | `/api/products/{id}/` | 查看商品詳情 |
| PATCH  | `/api/products/{id}/` | 商家修改商品 |
| DELETE | `/api/products/{id}/` | 商家刪除商品 |
🛒 Order API（開發中）

🚀 API Request / Response 範例
## 🔑 Auth 認證 API
### 1️⃣ 註冊 Register
Endpoint
POST /member/register/

Request Body
{
  "username": "john123",
  "password": "test1234",
  "email": "john@test.com",
  "role": "member"
}

Success Response
{
  "id": 5,
  "username": "john123",
  "email": "john@test.com",
  "role": "member"
}

### 2️⃣ 登入 Login
Endpoint
POST /member/login/

Request Body
{
  "username": "john123",
  "password": "test1234"
}

Success Response
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc2NTI3NDM2NywiaWF0IjoxNzY1MTg3OTY3LCJqdGkiOiI1YmJiMzI1OGU4ZjA0ODMxYjZlNjAxZDNiYTZkZDE1ZiIsInVzZXJfaWQiOiIyIiwicm9sZSI6Im1lbWJlciJ9.WjygWAY90Fn09n9_XnjaFkvVRdAPR0S9sAJTbduq1tM",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzY1MTg4MjY3LCJpYXQiOjE3NjUxODc5NjcsImp0aSI6Ijg3NDQ1OWMxY2Q1NzRmN2ZiMTMxY2UwMjJkMTY2YzM3IiwidXNlcl9pZCI6IjIiLCJyb2xlIjoibWVtYmVyIn0._DGZPppfd09Vbwr1tX_Vgk8SO8my2z-9Mivld0XGs7k",
  "username": "john123",
  "role": "member"
}

## 👤 Member 會員 API
Endpoint
GET /api/members/{id}/
⭕ 只能查看自己的資料（IsOwnerOfMemberProfile）

Example
GET /member/members/1/

Success Response
{
  "name": "John",
  "birthday": "2025-01-01",
  "orders": [
    {
      "member": 1,
      "created_at": "2025-12-07T22:52:16.966555+08:00",
      "status": "pending",
      "items": [
        {
          "product_name": "Q彈潔牙骨",
          "product_price": "2.99",
          "quantity": 2,
          "item_subtotal": 5.98
        },
        {
          "product_name": "雞肉鴨肉狗糧",
          "product_price": "6.99",
          "quantity": 1,
          "item_subtotal": 6.99
        }
      ],
      "total_price": 12.97
    }
  ],
  "last_update": "2025-12-08T18:03:34.595867+08:00",
  "member_points": 60,
  "login_days": 5,
  "last_loginDate": "2025-12-08T18:03:34.595867+08:00"
}

### 4️⃣ 更新自己的會員資料
PATCH /member/members/{id}/
Request Body
{
  "name": "John Wu"
}

Success Response
{
  "name": "John",
  "birthday": "2025-01-01",
  "orders": [
    {
      "member": 1,
      "created_at": "2025-12-07T22:52:16.966555+08:00",
      "status": "pending",
      "items": [
        {
          "product_name": "Q彈潔牙骨",
          "product_price": "2.99",
          "quantity": 2,
          "item_subtotal": 5.98
        },
        {
          "product_name": "雞肉鴨肉狗糧",
          "product_price": "6.99",
          "quantity": 1,
          "item_subtotal": 6.99
        }
      ],
      "total_price": 12.97
    }
  ],
  "last_update": "2025-12-08T18:03:34.595867+08:00",
  "member_points": 60,
  "login_days": 5,
  "last_loginDate": "2025-12-08T18:03:34.595867+08:00"
}

## 🏬 Store 商店 API
### 5️⃣ 商家建立商店
Endpoint
POST /store/stores/
⭕ 必須是登入後的商家（IsMerchant）
⭕ 每個商家只能建立一間商店（系統自動限制）

Request Body
{
  "name": "Apple Shop",
  "description": "Premium electronics and accessories."
}

Success Response
{
  "merchant": 1,
  "name": "帶帶黑狗的店",
  "description": "這是一家黑狗帶帶很愛的店喔！",
  "address": "高雄市高雄區高雄街100號10樓",
  "created_at": "2025-12-02T19:57:27.396909+08:00",
  "last_update": "2025-12-02T20:05:23.037647+08:00",
  "products": [
    {
      "description": "領帶超愛的潔牙骨",
      "name": "Q彈潔牙骨",
      "price": "2.99",
      "stock": 8
    },
    {
      "description": "領帶超愛的羈押狗糧",
      "name": "雞肉鴨肉狗糧",
      "price": "6.99",
      "stock": 19
    }
  ]
}

### 6️⃣ 查看商店列表（公開）
GET /store/stores/
Response
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "merchant": 1,
      "name": "帶帶黑狗的店",
      "description": "這是一家黑狗帶帶很愛的店喔！",
      "address": "高雄市三民區大連街373號6樓",
      "created_at": "2025-12-02T19:57:27.396909+08:00",
      "last_update": "2025-12-02T20:05:23.037647+08:00",
      "products": [
        {
          "description": "領帶超愛的潔牙骨",
          "name": "Q彈潔牙骨",
          "price": "2.99",
          "stock": 8
        },
        {
          "description": "領帶超愛的羈押狗糧",
          "name": "雞肉鴨肉狗糧",
          "price": "6.99",
          "stock": 19
        }
      ]
    }
  ]
}

### 7️⃣ 更新自己的商店
PATCH /store/stores/{id}/
⭕ 只能修改自己的商店（IsOwnerOfStore）

Request Body
{
  "description": "Best electronics with warranty."
}

Response
{
  "merchant": 1,
  "name": "帶帶黑狗的店",
  "description": "Best electronics with warranty."",
  "address": "高雄市高雄區高雄街100號10樓",
  "created_at": "2025-12-02T19:57:27.396909+08:00",
  "last_update": "2025-12-02T20:05:23.037647+08:00",
  "products": [
    {
      "description": "領帶超愛的潔牙骨",
      "name": "Q彈潔牙骨",
      "price": "2.99",
      "stock": 8
    },
    {
      "description": "領帶超愛的羈押狗糧",
      "name": "雞肉鴨肉狗糧",
      "price": "6.99",
      "stock": 19
    }
  ]
}

## 📦 Product 商品 API
Endpoint
POST /store/products/
⭕ 必須為商家 & 已建立商店

Request Body
{
  "name": "雞肉鴨肉狗糧",
  "description": "領帶超愛的羈押狗糧"
  "price": "79.00",
  "stock": 30
}

Success Response
{
  "description": "領帶超愛的羈押狗糧"
  "name": "雞肉鴨肉狗糧",
  "price": "79.00",
  "stock": 30
}

### 9️⃣ 查看商品列表（公開）
GET /store/products/
Response
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "description": "領帶超愛的潔牙骨",
      "name": "Q彈潔牙骨",
      "price": "2.99",
      "stock": 8
    },
    {
      "description": "領帶超愛的羈押狗糧",
      "name": "雞肉鴨肉狗糧",
      "price": "6.99",
      "stock": 19
    },
    {
      "description": "領帶沒有很愛",
      "name": "牛肉骰子",
      "price": "10.99",
      "stock": 15
    }
  ]
}

### 🔟 修改商品（限 owner）
PATCH /store/products/{id}/
Request Body
{
  "stock": 25
}

Response
{
  "description": "領帶超愛的羈押狗糧"
  "name": "雞肉鴨肉狗糧",
  "price": "79.00",
  "stock": 15
}



🧪 測試 Test（待補）

📌 專案 Roadmap（即將進行）
 完整訂單 API

 JWT Token 統一登入

 Media / 圖片上傳（商品圖片、會員頭像）

 Swagger / drf-spectacular

 Docker 部署

 ERD 圖正式化

 前後端分離 Demo（可選）

 📜 License
 MIT License