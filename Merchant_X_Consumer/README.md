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
##  Auth 認證 API
### 1 註冊 Register
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

### 2 登入 Login
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

## Member 會員 API
### 3 會員資料查詢
GET /member/members/{id}/
⭕ 只能查看自己的資料（IsOwnerOfMemberProfile）

Example
GET /member/members/1/

Success Response
{
  "name": "John",
  "birthday": "2025-01-01",
  "member_avatar": "empty.png",
  "address": "高雄市高雄區高雄路100號",
  "phone_num": "0912345678",
  "orders": [
    {
      "order_number": "ORD20251213-779524",
      "member": 1,
      "receiver_name": "John",
      "receiver_phone": "0912345678",
      "address": "高雄市高雄區高雄路100號",
      "note": "",
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

### 4 更新自己的會員資料
PATCH /member/members/{id}/
Request Body
{
  "name": "John Wu"
}

Success Response
{
  "name": "John Wu",
  "birthday": "2025-01-01",
  "member_avatar": "empty.png",
  "address": "高雄市高雄區高雄路100號",
  "phone_num": "0912345678",
  "orders": [
    {
      "order_number": "ORD20251213-779524",
      "member": 1,
      "receiver_name": "John",
      "receiver_phone": "0912345678",
      "address": "高雄市高雄區高雄路100號",
      "note": "",
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

## Store 商店 API
### 5 商家建立商店
POST /store/stores/
⭕ 必須是登入後的商家（IsMerchant）
⭕ 每個商家只能建立一間商店（系統自動限制）

Request Body
{
  "name": "帶帶黑狗的店",
  "description": "這是一家黑狗帶帶很愛的店喔！",
  "address": "高雄市高雄區高雄街100號10樓"
}

Success Response
{
  "merchant": 1,
  "name": "帶帶黑狗的店",
  "description": "這是一家黑狗帶帶很愛的店喔！",
  "address": "高雄市高雄區高雄街100號10樓",
  "created_at": "2025-12-02T19:57:27.396909+08:00",
  "last_update": "2025-12-02T20:05:23.037647+08:00",
  "products": []
}

### 6 查看商店列表（公開）
GET /store/stores/
Success Response
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "merchant": 1,
      "name": "帶帶黑狗的店",
      "description": "這是一家黑狗帶帶很愛的店喔！",
      "address": "高雄市高雄區高雄街10號10樓",
      "created_at": "2025-12-13T15:13:04.136497+08:00",
      "last_update": "2025-12-13T15:15:19.303452+08:00",
      "products": [
        {
          "description": "領帶沒有很愛",
          "name": "牛肉骰子",
          "price": "10.99",
          "stock": 12
        },
        {
          "description": "含有豐富雞肉與鴨肉的狗糧",
          "name": "羈押狗糧",
          "price": "7.99",
          "stock": 0
        },
        {
          "description": "讓帶帶牙齒乾淨溜溜的潔牙骨",
          "name": "Q彈潔牙骨",
          "price": "5.99",
          "stock": 20
        },
        {
          "description": "讓皮膚發亮的狗糧",
          "name": "鮭魚凍乾糧",
          "price": "7.99",
          "stock": 13
        }
      ]
    },
    {
      "merchant": 2,
      "name": "有條白色領帶的黑狗的店",
      "description": "這是一家黑狗有白色領帶很愛的店喔！",
      "address": "高雄市高雄區高雄街20號10樓",
      "created_at": "2025-12-13T15:13:04.136497+08:00",
      "last_update": "2025-12-13T15:17:47.797501+08:00",
      "products": [
        {
          "description": "濃郁奶香Q彈潔牙骨",
          "name": "牛奶潔牙骨",
          "price": "6.99",
          "stock": 23
        },
        {
          "description": "濃郁起司，狗狗peace",
          "name": "起司凍乾",
          "price": "5.99",
          "stock": 35
        }
      ]
    }
  ]
}

### 7 更新自己的商店
PATCH /store/stores/{id}/
⭕ 只能修改自己的商店（IsOwnerOfStore）

Request Body
{
  "address": "高雄市高雄區高雄街100號10樓"
}

Success Response
{
  "merchant": 1,
  "name": "帶帶黑狗的店",
  "description": "這是一家黑狗帶帶很愛的店喔！",
  "address": "高雄市高雄區高雄街100號10樓",
  "created_at": "2025-12-13T15:13:04.136497+08:00",
  "last_update": "2025-12-13T16:41:19.168678+08:00",
  "products": [
    {
      "description": "領帶沒有很愛",
      "name": "牛肉骰子",
      "price": "10.99",
      "stock": 12
    },
    {
      "description": "含有豐富雞肉與鴨肉的狗糧",
      "name": "羈押狗糧",
      "price": "7.99",
      "stock": 0
    },
    {
      "description": "讓帶帶牙齒乾淨溜溜的潔牙骨",
      "name": "Q彈潔牙骨",
      "price": "5.99",
      "stock": 20
    },
    {
      "description": "讓皮膚發亮的狗糧",
      "name": "鮭魚凍乾糧",
      "price": "7.99",
      "stock": 13
    }
  ]
}

## Product 商品 API
### 8 商家新增商品
POST /store/products/
⭕ 必須為商家 & 已建立商店

Request Body
{
    "name": "起司凍乾",
    "description": "濃郁起司，狗狗peace",
    "price": 5.99,
    "stock": 35
}

Success Response
{
    "name": "起司凍乾",
    "description": "濃郁起司，狗狗peace",
    "price": 5.99,
    "stock": 35
}

### 9 查看商品列表（公開）
GET /store/products/
Response
{
  "count": 6,
  "next": "http://127.0.0.1:8000/store/products/?page=2",
  "previous": null,
  "results": [
    {
      "description": "領帶沒有很愛",
      "name": "牛肉骰子",
      "price": "10.99",
      "stock": 12
    },
    {
      "description": "含有豐富雞肉與鴨肉的狗糧",
      "name": "羈押狗糧",
      "price": "7.99",
      "stock": 0
    },
    {
      "description": "讓帶帶牙齒乾淨溜溜的潔牙骨",
      "name": "Q彈潔牙骨",
      "price": "5.99",
      "stock": 20
    },
    {
      "description": "讓皮膚發亮的狗糧",
      "name": "鮭魚凍乾糧",
      "price": "7.99",
      "stock": 13
    },
    {
      "description": "濃郁奶香Q彈潔牙骨",
      "name": "牛奶潔牙骨",
      "price": "6.99",
      "stock": 23
    }
  ]
}

### 10 修改商品（限 owner）
PATCH /store/products/{id}/
Request Body
{
  "stock": 20
}

Success Response
{
  "description": "含有豐富雞肉與鴨肉的狗糧",
  "name": "羈押狗糧",
  "price": "7.99",
  "stock": 20
}

## Order 訂單處理 API
### 11 訂單詳細資料
GET /store/orders/{id}/
Success Response
{
  "order_number": "ORD20250225-00123",
  "member": 17,
  "receiver_name": "王小明",
  "receiver_phone": "0912345678",
  "address": "台北市信義區松智路 1 號",
  "note": "請於晚上 6 點後送達",
  "created_at": "2025-02-25T10:32:11Z",
  "status": "pending",
  "items": [
    {
      "product_name": "高山烏龍茶禮盒",
      "product_price": "550.00",
      "quantity": 2,
      "item_subtotal": "1100.00"
    },
    {
      "product_name": "100% 純蜂蜜",
      "product_price": "300.00",
      "quantity": 1,
      "item_subtotal": "300.00"
    }
  ],
  "total_amount": "1400.00"
}

### 12 建立訂單成功回傳
POST /store/orders/
Request Body
{
  "receiver_name": "王小明",
  "receiver_phone": "0912345678",
  "address": "台北市信義區松智路 1 號",
  "note": "請用紙箱包裝",
  "items": [
    { "product": 5, "quantity": 2 },
    { "product": 9, "quantity": 1 }
  ]
}

Success Response
{
  "order_number": "ORD20250225-00124",
  "member": 17,
  "receiver_name": "王小明",
  "receiver_phone": "0912345678",
  "address": "台北市信義區松智路 1 號",
  "note": "請用紙箱包裝",
  "status": "pending",
  "items": [
    {
      "product_name": "高山烏龍茶禮盒",
      "product_price": "550.00",
      "quantity": 2,
      "item_subtotal": "1100.00"
    },
    {
      "product_name": "100% 純蜂蜜",
      "product_price": "300.00",
      "quantity": 1,
      "item_subtotal": "300.00"
    }
  ],
  "total_amount": "1400.00"
}

### 13 修改訂單（會員修改地址、商家修改狀態）
PATCH /store/orders/{id}/
Request Body（會員更新地址）
{
  "address": "台北市大安區忠孝東路三段 200 號"
}

Success Response
{
  "order_number": "ORD20250225-00124",
  "member": 17,
  "receiver_name": "王小明",
  "receiver_phone": "0912345678",
  "address": "台北市大安區忠孝東路三段 200 號",
  "note": "請用紙箱包裝",
  "created_at": "2025-02-25T10:35:14Z",
  "status": "pending",
  "items": [
    {
      "product_name": "高山烏龍茶禮盒",
      "product_price": "550.00",
      "quantity": 2,
      "item_subtotal": "1100.00"
    },
    {
      "product_name": "100% 純蜂蜜",
      "product_price": "300.00",
      "quantity": 1,
      "item_subtotal": "300.00"
    }
  ],
  "total_amount": "1400.00"
}

Request Body（商家更新狀態 → paid）
{
  "status": "paid"
}

Success Response
{
  "order_number": "ORD20250225-00124",
  "status": "paid",
  "total_amount": "1400.00"
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