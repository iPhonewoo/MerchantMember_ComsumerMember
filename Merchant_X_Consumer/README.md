# Merchant X Consumer API

  一個簡單的「多商家 x 會員」電商後端專案，使用 **Django + Django REST Framework** 實作，包含：
    A. 使用者註冊 / 登入（JWT）
    B. 會員 / 商家角色分離
    C. 商店管理、商品管理
    D. 訂單建立 / 查詢 / 狀態更新
    E. 權限控管與訂單狀態機制

---

## 技術棧

  - Python 3.x
  - Django
  - Django REST Framework
  - djangorestframework-simplejwt
  - django-filter
  - drf-spectacular（自動產生 OpenAPI / Swagger 文件）
  - SQLite（開發環境）

---

## 專案結構

  ```text
  Merchant_X_Consumer/
  ├── member/
  │   ├── models.py       # User / Member / Merchant
  │   ├── serializers.py  # Register / Login / MemberSerializer
  │   ├── views.py        # 註冊、登入、會員 Profile API
  │   ├── permissions.py  # 角色 & 擁有者權限
  │   └── urls.py
  ├── store/
  │   ├── models.py       # Store / Product / Order / OrderItem
  │   ├── serializers.py  # Product / Store / Order 序列化
  │   ├── views.py        # 商店、商品、訂單 API
  │   ├── filter.py       # 產品篩選相關
  │   └── urls.py
  ├── config/
  │   ├── settings.py
  │   ├── urls.py
  │   └── ...
  └── README.md


使用者角色說明

  | 角色                | 能力                                               |
  | --------------------| --------------------------------------------------|
  | **Admin**           | 可在 Django admin 後台管理所有資料                  |
  | **Merchant（商家）** | 可以管理自己商店 & 商品、查看包含自己商品的訂單、出貨 |
  | **Member（會員）**   | 可以下單、查看自己的訂單、查看產品                   |
  | **訪客**             | 只能瀏覽公開商品與商店                             |


資料庫 ERD

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


安裝與啟動
  # 1. 建立虛擬環境
    python -m venv venv
    source venv/bin/activate  # Windows: venv\Scripts\activate

  # 2. 安裝套件
    pip install -r requirements.txt

  # 3. 建立資料庫
    python manage.py migrate

  # 4. 建立超級管理員（可選）
    python manage.py createsuperuser

  # 5. 啟動開發伺服器
    python manage.py runserver


JWT 認證流程

  1. 註冊帳號
  2. 使用 /member/login/ 取得 access & refresh token
  3. 呼叫需要登入的 API，在 Header 加上：
    Authorization: Bearer <your_access_token>


API 文件
  Auth
    | Method | Path         | 說明         |
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


API Request / Response 範例
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

  ## Product 商品 API
    ### 8 商家新增商品
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
          "status": "pending",
          "payment_method": "unpaid",
          "receiver_name": "王小明",
          "receiver_phone": "0912345678",
          "address": "台北市大安區忠孝東路三段 200 號",
          "note": "請用紙箱包裝",
          "created_at": "2025-02-25T10:35:14Z",
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

  ## 狀態變更 action
    ### 14 付款
      POST /store/orders/{id}/pay/
        {
          "detail": "付款成功",
          "status": "paid"
        }

    ### 15 出貨
      POST /store/orders/{id}/ship/
        {
          "detail": "出貨狀態已更新",
          "status": "shipped"
        }

    ### 16取消訂單
      POST /store/orders/{id}/cancel/
        {
          "detail": "訂單已取消",
          "status": "canceled"
        }



測試 Test（即將完成）


專案 Roadmap（準備進行）

  A. Media / 圖片上傳（商品圖片、會員頭像）
  B. Swagger / drf-spectacular


Docker 開發流程（Development with Docker）

  本專案使用 Docker + Docker Compose 作為主要開發與測試環境，確保：
    A. 本機環境一致
    B. CI / CD 與本地行為相同
    C. 降低「我本機可以、你那邊不行」的風險

  環境需求

    A. Docker Desktop
    B. Docker Compose（v2）

  啟動專案（第一次或 Docker 設定有變更）

    docker compose up --build

    或背景執行：
    docker compose up -d --build

  資料庫遷移（在容器內）

    docker compose exec web python manage.py migrate

  執行測試（推薦方式）

    docker compose exec web pytest
    ⚠️ 請勿直接在本機執行 pytest
    Django 專案實際執行環境為 Docker container

  停止服務

    docker compose down

  Docker + CI（GitHub Actions）

    本專案已設定 GitHub Actions：
      A. 每次 push / pull request 自動執行測試
      B. 驗證 migration + pytest 是否通過
      C. 作為品質保證（Quality Gate）


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


 License
 MIT License

