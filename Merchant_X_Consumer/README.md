Merchant X Consumer API
  一個「多商家 x 會員」的電商後端 API 專案，使用 Django + Django REST Framework 實作，
  以實際商業系統為設計目標，完整涵蓋：

    1. 多角色架構與權限控管
    2. 訂單流程與狀態機
    3. 併發安全（庫存）
    4. 商家視角 Analytics（PostgreSQL 驗證）
    5. 完整自動化測試與 CI

  本專案不只是 CRUD，而是可擴充、可測試、可交付的後端系統設計。

---

技術棧
  Core Backend

    1. Python 3.11
    2. Django
    3. Django REST Framework

  Authentication / Authorization

    1. JWT Authentication (djangorestframework-simplejwt)
    2. Custom Permission Classes（Role-based & Object-level）

  API Tooling

    1. django-filter
    2. drf-spectacular (OpenAPI / Swagger)

  Database

    1. SQLite（Local Development）
    2. PostgreSQL（Production / Render）
    - Database configuration is environment-based (12-factor app compliant)

  Testing

    1. pytest
    2. pytest-django
    3. factory_boy
    4. GitHub Actions（CI）
    5. PostgreSQL-powered Analytics Tests

  Containerization

    1. Docker
    2. Docker Compose (local development & CI alignment)

---

專案結構（依責任劃分，符合 Django app best practices）

    .github/workflows/tests.yml   # GitHub Actions CI pipeline
    Merchant_X_Consumer/
    ├── member/
    │   └── ...
    ├── store/
    │   │   └── analytics/
    │   │       └── services/
    │   │           └── tests/
    │   └── ...
    ├── Merchant_X_Consumer/
    │   └── settings.py
    ├── tests/                        # API / permission / workflow tests
    │   ├── conftest.py
    │   ├── factories/
    │   │   ├── user_factory.py
    │   │   ├── store_factory.py
    │   │   ├── product_factory.py
    │   │   └── order_factory.py
    │   ├── members/
    │   │   ├── test_member_login.py
    │   │   └── test_member_profile.py
    │   ├── stores/
    │   │   ├── test_product_crud.py
    │   │   └── test_store_crud.py
    │   └── orders/
    │       ├── test_order_create.py
    │       ├── test_order_permissions.py
    │       └── test_order_update.py
    ├── docker-compose.yml
    ├── Dockerfile
    ├── pytest.ini
    ├── requirements.txt
    └── README.md

---

使用者角色說明

  | 角色                | 能力                                               |
  | --------------------| --------------------------------------------------|
  | Admin               | 可在 Django admin 後台管理所有資料                  |
  | Merchant（商家）     | 可以管理自己商店 & 商品、查看包含自己商品的訂單、出貨 |
  | Member（會員）       | 可以下單、查看自己的訂單、查看產品                   |
  | Visitor                 | 只能瀏覽公開商品與商店                             |

---

資料庫 ERD

  以下是目前模型結構：

    User (Django auth user)
    │
    ├── Member (OneToOne)
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

---

安裝與啟動
  1. 建立虛擬環境
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate
  2. 安裝套件
    pip install -r requirements.txt
  3. 建立資料庫
    python manage.py migrate
  4. 建立超級管理員（可選）
    python manage.py createsuperuser
  5. 啟動開發伺服器
    python manage.py runserver

---

JWT 認證流程

  1. 註冊帳號
  2. 使用 /member/login/ 取得 access & refresh token
  3. 呼叫需要登入的 API，在 Header 加上：
    Authorization: Bearer <your_access_token>

---

API 文件

Complete API documentation is available via Swagger (drf-spectacular)

  Auth

    | Method | Path             | 說明         |
    | ------ | ---------------- | ---------- |
    | POST   | `/member/register/` | 註冊         |
    | POST   | `/member/login/`    | 登入取得 Token |

  Member API

    | Method | Path             | 說明             |
    | ------ | -------------------- | -------------- |
    | GET    | `/member/members/{id}/` | 查看自己的會員資料（需登入） |
    | PATCH  | `/member/members/{id}/` | 更新自己的資料        |
    | PUT    | `/member/members/{id}/` | 完整更新資料         |

  Store API

    | Method | Path                  | 說明              |
    | ------ | --------------------- | ----------------- |
    | POST   | `/store/stores/`      | 商家建立商店（每商家只能一間） |
    | GET    | `/store/stores/`      | 查看所有商店          |
    | GET    | `/store/stores/{id}/` | 查看單一商店          |
    | PATCH  | `/store/stores/{id}/` | 商家修改自己的商店       |
    | DELETE | `/store/stores/{id}/` | 刪除（限 owner）     |

  Product API

    | Method | Path                    | 說明     |
    | ------ | ----------------------- | -------- |
    | POST   | `/store/products/`      | 商家新增商品 |
    | GET    | `/store/products/`      | 查看商品列表 |
    | GET    | `/store/products/{id}/` | 查看商品詳情 |
    | PATCH  | `/store/products/{id}/` | 商家修改商品 |
    | DELETE | `/store/products/{id}/` | 商家刪除商品 |

  Order API

    | Method | Path                         | 說明                | 權限                    |
    | ------ | ---------------------------- | ----------------- | --------------------- |
    | POST   | `/store/orders/`             | 建立訂單              | 已登入會員 (`member`)      |
    | GET    | `/store/orders/`             | 查看訂單列表            | 已登入會員/商家/管理員          |
    | GET    | `/store/orders/{id}/`        | 查看單筆訂單詳細          | 該會員自身 / 該訂單相關商家 / 管理員 |
    | PATCH  | `/store/orders/{id}/`        | 更新收件資料或狀態         | 訂單本人（收件資料）、商家 (部分情境)  |
    | DELETE | `/store/orders/{id}/`        | 取消 / 刪除訂單         | 訂單本人 / 管理員            |
    | POST   | `/store/orders/{id}/pay/`    | 付款（狀態改為 paid）     | 該訂單會員本人               |
    | POST   | `/store/orders/{id}/ship/`   | 出貨（狀態改為 shipped）  | 擁有該訂單商品的商家            |
    | POST   | `/store/orders/{id}/cancel/` | 取消訂單（改為 canceled） | 該訂單會員本人               |

---

API Request / Response 範例
  ##  Auth 認證 API
    ### 註冊 Register
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

    ### 登入 Login
      POST /member/login/

        Request Body
        {
          "username": "john123",
          "password": "test1234"
        }

        Success Response
        {
          "access": "<jwt_access_token>",
          "username": "john123",
          "role": "member"
        }

  ## Member 會員 API
    ### 會員資料查詢
      GET /member/members/{id}/
      只能查看自己的資料（IsOwnerOfMemberProfile）

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
              "status": "pending",
              "total_price": 12.97
            }
          ],
          "last_update": "2025-12-08T18:03:34.595867+08:00",
          "member_points": 60,
          "login_days": 5,
          "last_loginDate": "2025-12-08T18:03:34.595867+08:00"
        }

    ### 更新自己的會員資料
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

        403 Forbidden(非該會員修改該會員資料)
        {
          "detail": "You do not have permission to perform this action."
        }

  ## Store 商店 API
    ### 商家建立商店
      POST /store/stores/
      必須是登入後的商家（IsMerchant）
      每個商家只能建立一間商店（系統自動限制）

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

    ### 更新自己的商店
      PATCH /store/stores/{id}/
      只能修改自己的商店（IsOwnerOfStore）

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

        403 Forbidden(非商家擁有者)


  ## Product 商品 API
    ### 商家新增商品
      POST /store/products/
      必須為商家 & 已建立商店

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

    ### 查看商品列表（公開）
      GET /store/products/ （公開商品列表，支援分頁）


    ### 修改商品（限 owner）
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

        403 Forbidden(非商家修改)
        {
          "detail": "You do not have permission to perform this action."
        }

  ## Order 訂單處理 API
    ### 訂單詳細資料
      GET /store/orders/{id}/
        Success Response
        {
          "order_number": "ORD20250225-00123",
          "member": 17,
          "status": "pending",
          "payment_method": "unpaid",
          "receiver_name": "王小明",
          "receiver_phone": "0912345678",
          "address": "台北市信義區松智路 1 號",
          "note": "請於晚上 6 點後送達",
          "created_at": "2025-02-25T10:32:11Z",
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

    ### 建立訂單成功回傳
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
          "status": "pending",
          "payment_method": "unpaid",
          "receiver_name": "王小明",
          "receiver_phone": "0912345678",
          "address": "台北市信義區松智路 1 號",
          "note": "請用紙箱包裝",
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

    ### 修改訂單（會員修改地址、商家修改狀態）
      PATCH /store/orders/{id}/
        Member：更新收件資訊
        Merchant：更新訂單狀態（paid / shipped）

        Success Response
        {
          "order_number": "ORD20250225-00124",
          "status": "paid",
          "total_amount": "1400.00"
        }

  ## 狀態變更 Actions（Business Workflow）
    ### 付款
      POST /store/orders/{id}/pay/
    ### 出貨
      POST /store/orders/{id}/ship/
    ### 取消訂單
      POST /store/orders/{id}/cancel/

---

Database Strategy（This project follows the 12-Factor App methodology by separating configuration from code.）
  
  本專案在不同環境使用不同資料庫，以兼顧開發效率與正式環境穩定性，採用 環境變數切換資料庫策略。

  為什麼本機使用 SQLite？

    在本機開發與測試階段，本專案使用 SQLite：
    1. 不需額外安裝資料庫服務
    2. 設定簡單、啟動快速
    3. 適合 migrations、單元測試（pytest）
    這讓開發者可以專注在 商業邏輯與 API 設計，而非環境設定。

  為什麼部署環境改用 PostgreSQL？

    在正式部署（Render）環境，本專案改用 PostgreSQL：
      1. Render 容器為短生命週期（ephemeral）
      2. SQLite 為檔案型資料庫，重啟後資料可能遺失
      3. PostgreSQL 為獨立資料庫服務，資料可持久保存
    因此正式環境必須使用 PostgreSQL 以確保資料安全與一致性。

  技術實作方式

    本專案使用 dj-database-url 來根據 環境變數自動切換資料庫，不需修改任何程式碼邏輯。

  Render 環境設定

    在 Render Web Service 中設定以下 Environment Variables：

    | Name                     | Value                          |
    | ------------------------ | ------------------------------ |
    | `DATABASE_URL`           | Render 提供的 PostgreSQL 連線字串     |
    | `DJANGO_SETTINGS_MODULE` | `Merchant_X_Consumer.settings` |
    | `SECRET_KEY`             | Django secret key              |
    | `DEBUG`                  | `False`                        |

  部署時 Render 會自動：

    1. 安裝 PostgreSQL driver（psycopg2-binary）
    2. 連線至 PostgreSQL
    3. 執行 python manage.py migrate
    4. 啟動 Django API

  成功驗證方式

    正式部署後，透過以下方式確認 PostgreSQL 已成功啟用：
      1. Render 服務重啟後，已建立的使用者 / 商家帳號仍可正常登入
      2. 資料在服務重啟後仍存在，確認使用的是持久化資料庫

---

Testing Strategy
  本專案已建立 完整的自動化測試流程，確保核心商業邏輯與權限控制的正確性。

  測試工具

    1. pytest
    2. pytest-django
    3. factory_boy
    4. Django Test Client / DRF APIClient

  測試設計原則

    1. 每個角色行為皆有測試（Member / Merchant / Admin）
    2. 權限為第一優先測試項目
    3. 測試專注在「業務邏輯是否正確」，而非實作細節

  測試內容涵蓋

    Member
      1. 會員註冊 / 登入
      2. 只能查看與修改自己的會員資料
      3. 無法存取其他會員資料

    Store / Product（Merchant）
      1. 商家只能建立一間商店
      2. 商家只能修改 / 刪除自己的商店與商品
      3. 無法操作其他商家的資源

    Order
      1. 會員可建立訂單
      2. 訂單建立時會檢查商品庫存
      3. 商家只能看到「包含自己商品」的訂單
      4. 訂單狀態變更遵守狀態轉移規則（Pending → Paid → Shipped → Completed）

  測試結構

    tests/
    ├── conftest.py          # 共用 fixtures（API client, user）
    ├── factories/           # factory_boy 建立測試資料
    │   ├── user_factory.py
    │   ├── merchant_factory.py
    │   └── store_factory.py
    ├── members/
    │   ├── test_member_login.py
    │   └── test_member_profile.py
    ├── stores/
    │   ├── test_store_crud.py
    │   └── test_product_crud.py
    └── orders/
        ├── test_order_create.py
        ├── test_order_update.py
        └── test_order_permissions.py

---

CI（Continuous Integration）

  本專案已整合 GitHub Actions：

    1. 每次 push / pull request 自動執行測試
    2. 驗證 migration + pytest 是否通過
    3. 作為品質保證（Quality Gate）
    確保任何變更都不會破壞既有功能。

  為什麼這樣設計？

    1. 本機、CI、正式環境設定一致
    2. DB 設定與程式碼分離（符合 12-factor app）
    3. 測試可快速驗證商業規則與權限安全性
    4. 部署流程可重現、可擴充

---

Docker 開發流程（Development with Docker）

  本專案使用 Docker + Docker Compose 作為主要開發與測試環境，確保：

    1. 本機環境一致
    2. CI / CD 與本地行為相同
    3. 降低「我本機可以、你那邊不行」的風險

  環境需求

    1. Docker Desktop
    2. Docker Compose（v2）

  啟動專案（第一次或 Docker 設定有變更）

    docker compose up --build

    或背景執行：
    docker compose up -d --build

  資料庫遷移（在容器內）

    docker compose exec web python manage.py migrate

  執行測試

    docker compose exec web pytest
    ⚠️ 請勿直接在本機執行 pytest
    Django 專案實際執行環境為 Docker container

  停止服務

    docker compose down

---

Technical Highlights（技術亮點）

  1. Multi-Role Architecture（多角色架構設計）

    本專案採用 單一 User + 角色分離（Role-based Design） 架構：
      A. User：認證、JWT、身份來源
      B. Member：一般消費者（下單、會員資料）
      C. Merchant：商家（商店、商品、訂單處理）
      D. Admin：系統管理（Django Admin）

        User
        ├── Member (OneToOne)
        └── Merchant (OneToOne)

    優點
      A. 避免 User model 過度膨脹
      B. 角色責任明確，易於擴充
      C. 權限與商業邏輯清楚分離

  2. Object-Level Permission Control（物件層級權限控管）

    不僅檢查是否登入，還嚴格驗證「是否為資源擁有者」：
      A. 商家只能修改 自己的商店
      B. 會員只能查看 自己的訂單
      C. 商家只能看到 包含自己商品的訂單

    所有權限邏輯集中於 permissions.py，避免散落在 View 中，提高可維護性與可測試性。

  3. Order State Machine（訂單狀態機）

    訂單狀態並非任意修改，而是遵循明確狀態轉換規則：
      pending → paid → shipped → completed
        └──→ canceled

    狀態轉換邏輯集中於 Order.can_transition()，確保：
      A. 商業規則集中管理
      B. API / Admin / Background Job 可共用
      C. 狀態錯誤可即時阻擋

  4. Price Snapshot（購買當下價格鎖定）

    OrderItem 儲存 price_at_purchase，而非直接使用商品即時價格，確保：
      A. 商品價格變動不影響歷史訂單
      B. 訂單金額具備可追溯性
      C. 符合實際電商系統設計

  5. Concurrency-Safe Inventory Handling（高併發庫存安全）

    建立訂單時使用：
      A. transaction.atomic()
      B. select_for_update()

    避免多人同時下單造成庫存超賣，確保資料一致性。

  6. Clear Serializer Responsibility（序列化職責分離）

    針對不同 API 行為，使用不同 Serializer：
      A. OrderCreateSerializer：建立訂單
      B. OrderUpdateSerializer：更新狀態 / 收件資料
      C. OrderSerializer：純展示

    避免萬用 Serializer，讓每個 API 行為語意清楚。

  7. Automated Testing with pytest + factory_boy

    (1)使用 pytest + factory_boy
    (2)測試涵蓋：
      A. 權限邏輯
      B. 訂單流程
      C. 成功 / 失敗案例

    測試資料與實際資料完全隔離，確保專案具備長期維護能力。

  8. CI with GitHub Actions & Docker

    (1)Docker Compose 本地開發環境
    (2)GitHub Actions 自動執行：
      A. migration
      B. pytest
    (3)每次 push / PR 都會驗證專案穩定性

  總結
  本專案不只是 CRUD，而是完整模擬實際電商系統的 角色、權限、狀態、併發、測試與交付流程。

---

Analytics Module（Merchant-facing）

本專案包含一組 獨立、可測試、以商家視角為核心的 Analytics 模組，
用於商家後台營運分析，而非平台總覽報表。

  設計定位

    1. 分析視角：Merchant（單一商家）
    2. 資料來源：僅統計該商家所屬的 OrderItem
    3. 驗證方式：PostgreSQL + CI
  
  核心設計原則

    1. GMV 計算來源明確

      GMV = Σ (OrderItem.price_at_purchase × quantity)

      A. 不使用 Order.total_amount
      B. 避免多商家訂單金額混用
  
    2. 訂單數一律防 JOIN 放大

      Count(Order.id, distinct=True)

    3. ORM 計算心法

      A. 先 annotate（row-level）
      B. 再 aggregate / values（group-level）
      C. 金額運算使用 ExpressionWrapper
          - 避免 Sum(F() * F()) ORM error

    4. 狀態預設排除 canceled

      A. canceled 不計入 GMV / order count / timeseries
      B. 但保留 status filter 彈性

  Analytics Services

    | Service                | 說明                                         |
    | ---------------------- | ------------------------------------------ |
    | build_order_summary    | order_count / gmv / aov / status_breakdown |
    | build_order_timeseries | day / month，支援 zero-fill                   |
    | build_top_products     | quantity / revenue / order_count           |
    | build_top_customers    | total_gmv / order_count / last_order_date  |

  Analytics API

    /merchant/analytics/order_summary
    /merchant/analytics/timeseries
    /merchant/analytics/top_products
    /merchant/analytics/top_customers

  Analytics Testing Strategy

    1. Analytics tests 全數使用 PostgreSQL
    2. CI 中獨立 job 驗證
    3. 測試重點：
      A. DISTINCT 防 JOIN 放大
      B. canceled 預設排除
      C. time-series zero-fill
      D. month grouping = 該月第一天
      E. 金額精準度

  Test Infrastructure 修正

    1. Order.created_at = auto_now_add=True
    2. Factory 預設會被忽略時間
    3. 已修正為允許 override，確保 time-based tests deterministic
      （屬 test infra fix，非功能變更）

---

Frontend Integration (API Consumer Validation)

  本專案包含一個最小化的前端應用，用於實際驗證後端 API 的可用性與設計合理性。

  前端定位說明：

    1. 前端僅作為 API Consumer 與流程驗證工具
    2. 不作為本專案的核心設計重點
    3. 所有商業邏輯、權限判斷與狀態控制皆由後端負責

  已驗證的前端流程包含：

    1. 使用者註冊 / 登入（JWT）
    2. Role-based 行為驗證（Member / Merchant）
    3. 商家商品上架
    4. 會員下單流程（Cart → Order → OrderItem）
    5. 訂單列表呈現（僅能查看自身訂單）
    6. DRF Pagination 實際前端消費（results / count）

    若要詳細了解Order介接流程及實際除錯經驗，請參考`docs/order-backend-notes.md`

  此前端實作主要用於驗證後端 API 在真實使用情境下的正確性與穩定性，
  並非本專案的核心設計重點。

---

專案 Roadmap（準備進行）

  1. Media / 圖片上傳（商品圖片、會員頭像）
  2. Swagger API 強化

---

License
 MIT License

