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

🧩 資料庫 ERD（v1）

以下是目前模型結構（後續我也可幫你畫成 ER 圖 PNG）：
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
📘 API 文件（第一版）
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