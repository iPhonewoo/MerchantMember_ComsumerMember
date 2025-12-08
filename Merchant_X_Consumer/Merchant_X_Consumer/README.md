# Merchant X Consumer — 多商家與會員系統 API

本專案是一個使用 **Django 5 + Django REST Framework** 打造的多商家與會員 API 系統。  
功能包含：

- 會員註冊 / 登入 / 個人資料管理
- 商家註冊 / 商店建立與維護
- 商品管理（商家才能新增／修改）
- 訂單系統（會員下單、商家查看與處理）
- 角色權限控管（Admin / Merchant / Member）
- Owner-Based Permission（只能操作自己的資料）
- Token 驗證（或 JWT 擴充）

此專案可作為：
- 電商後端  
- 多商家平台（Marketplace）  
- API backend 課程教材  
- 作品集（接案、面試使用）  

---

## 📦 專案技術棧

- Python 3.11+
- Django 5.x
- Django REST Framework
- SQLite（可替換為 PostgreSQL）
- Simple JWT（可選）
- Docker（可選 — 後續加入）
- drf-spectacular / Swagger（規劃中）

---

## 📁 專案結構說明

```bash
Merchant_X_Consumer/
│
├── member/               # 會員（Member）資料與 API
├── merchant/             # 商家（Merchant）資料與 API
├── store/                # 商店 Store + 商品 Product API
├── order/                # 訂單相關 API 與邏輯
│
├── config/               # Django 專案設定
├── requirements.txt      # 套件清單（建議加入）
├── README.md             # 本文件
└── manage.py
