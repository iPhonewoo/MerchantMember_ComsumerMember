# Order Creation – Backend Debug & Integration Notes

> **Scope:** Backend-only (Django REST Framework)
> 
> This document records a real-world debugging process and final design decisions for the **Order Creation API**. It focuses strictly on backend responsibilities, API contracts, and integration assumptions. Frontend implementation details are intentionally omitted.

---

## 1. API Overview

### Create Order

**Endpoint**
```
POST /store/orders/
```

**Authentication**
- JWT required
- Order ownership is determined by the authenticated user

---

## 2. API Contract (Client Requirements)

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

### Rules

- `items` must contain at least one element
- `product` must be a valid **Product ID** returned by the Product API
- `quantity` must be a positive integer
- `member` **must NOT** be provided by the client

---

## 3. Backend Responsibilities

The backend is designed to be **authoritative** and does not trust client-side calculations or ownership data.

- Validates all product IDs
- Validates stock availability
- Prevents overselling using database row locking (`select_for_update`)
- Calculates total order amount on the backend
- Associates order with the authenticated member
- Executes the entire order creation inside a database transaction

---

## 4. Key Debugging Lessons

### 4.1 Product ID Must Be Explicitly Exposed

**Root cause:**
- Product serializer did not expose `id`
- Client could not reference products correctly

**Fix:**
```python
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "stock"]
```

---

### 4.2 Nested Serializer ForeignKey Validation

Nested order item creation requires explicit FK handling.

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

### 4.3 `read_only_fields` Are Not in `validated_data`

- Fields marked as `read_only` never appear in `validated_data`
- Attempting to access them will raise `KeyError`

**Correct pattern:**

```python
serializer.save(member=request.user.member)
```

---

### 4.4 Correct DRF Lifecycle Usage

**Validation and persistence responsibilities:**

| Step | Responsibility |
|----|----|
| `serializer.is_valid()` | Data validation |
| `serializer.save()` | Object creation |
| View | Inject authenticated context |

---

## 5. Final Successful State

Example of validated backend data:

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
- Order created successfully
- OrderItems created successfully
- Stock decremented atomically
- Total amount calculated on backend

---

## 6. Design Philosophy

- Backend owns **data integrity**
- Client supplies references, not truth
- All critical calculations happen server-side
- API contracts are explicit and enforced

---

## 7. Interview-Ready Summary

This implementation demonstrates:

- Real-world DRF nested serializer usage
- Safe order creation with transactional integrity
- Clear backend–client contract boundaries
- Production-grade handling of concurrency and validation

---

✅ Order creation backend is complete, stable, and production-ready.

