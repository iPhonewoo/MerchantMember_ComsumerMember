# Order Creation – Backend Debug & Integration Notes

  Scope： 僅後端（Django REST Framework）

  本文件記錄了 訂單建立 API（Order Creation API） 在實務開發中實際遇到的除錯過程與最終設計決策。
  內容嚴格聚焦於 後端責任、API 合約（Contract）與前後端整合假設，刻意不包含任何前端實作細節。

---

## 1. API Overview

### 建立訂單（Create Order）

**Endpoint**
  ```
  POST /store/orders/
  ```

**身分驗證（Authentication）**
  A. 需使用 JWT
  B. 訂單所屬會員由「已驗證的使用者」自動決定

---

## 2. PI 合約（Client 端需求）

### Request Body

  ```json
  {
    "receiver_name": "string",
    "receiver_phone": "string",
    "address": "string",
    "note": "string",
    "items": [
      {
        "product": 1,
        "quantity": 2
      }
    ]
  }
  ```

### 規則（Rules）

  A. `items` 至少必須包含一筆資料
  B. `product` 必須是由 Product API 回傳的 有效 Product ID
  C. `quantity` 必須為 正整數
  D. `member` 禁止由 client 端傳入

---

## 3. 後端責任（Backend Responsibilities）

  後端設計採取 權威式（Authoritative） 原則，不信任任何 client 端的計算結果或身分資料。

  後端必須負責：
    A. 驗證所有 Product ID 是否存在
    B. 驗證商品庫存是否足夠
    C. 使用資料庫列鎖（select_for_update）防止超賣
    D. 在後端計算訂單總金額
    E. 將訂單關聯至當前登入的會員
    F. 將整個訂單建立流程包在資料庫交易（transaction）中執行

---

## 4. 關鍵除錯經驗（Key Debugging Lessons）

### 4.1 Product ID 必須明確對外提供

  問題根源（Root cause）：
    A. Product Serializer 未暴露 id
    B. Client 無法正確引用商品

**Fix:**
  ```python
  class ProductSerializer(serializers.ModelSerializer):
      class Meta:
          model = Product
          fields = ["id", "name", "price", "stock"]
  ```

---

### 4.2 Nested Serializer 的 ForeignKey 驗證

  建立訂單項目（OrderItem）時，巢狀 Serializer 必須明確處理 ForeignKey。

  ```python
  class OrderItemCreateSerializer(serializers.ModelSerializer):
      product = serializers.PrimaryKeyRelatedField(
          queryset=Product.objects.all()
      )

      class Meta:
          model = OrderItem
          fields = ["product", "quantity"]
  ```

---

### 4.3 read_only_fields 不會出現在 validated_data

  A. 被標記為 read_only 的欄位 永遠不會出現在 validated_data
  B. 嘗試直接存取會導致 KeyError

  正確做法：

  ```python
  serializer.save(member=request.user.member)
  ```

---

### 4.4 正確理解 DRF 的生命週期（Lifecycle）

  驗證與儲存責任分工：

  | 步驟                      | 責任           |
  | ----------------------- | ------------ |
  | `serializer.is_valid()` | 資料驗證         |
  | `serializer.save()`     | 建立資料         |
  | View                    | 注入已驗證的使用者上下文 |

---

## 5. 最終成功狀態（Final Successful State）

  後端實際驗證後的資料範例如下：

  ```python
  validated_data = {
    'receiver_name': 'fun',
    'receiver_phone': '0900',
    'address': 'kh',
    'note': 'ok',
    'items': [
      {'product': <Product: 牛肉骰子>, 'quantity': 1}
    ],
    'member': <Member: authenticated user>
  }
  ```

  Results:
    A. 訂單成功建立
    B. OrderItems 成功建立
    C. 庫存以原子性方式正確扣減
    D. 訂單總金額由後端計算完成

---

## 6. 設計理念（Design Philosophy）

  A. 後端負責 資料完整性（Data Integrity）
  B. Client 只提供「參考」，不提供「真相」
  C. 所有關鍵計算皆在 Server 端完成
  D. API 合約清楚定義並嚴格執行

---

## 7. 面試用摘要（Interview-Ready Summary）

  此實作展示了：

  A. 真實情境下的 DRF 巢狀 Serializer 應用
  B. 具備交易一致性的安全訂單建立流程
  C. 清楚劃分後端與 Client 的責任邊界
  D. 生產等級的併發控制與資料驗證設計

---

✅ 訂單建立後端功能已完成，穩定，並可直接用於正式環境（Production-ready）。

