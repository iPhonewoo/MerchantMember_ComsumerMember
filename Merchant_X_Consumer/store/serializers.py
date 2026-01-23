from django.db import transaction # 用於資料庫交易管理
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from store.models import Store, Product, Order, OrderItem
from datetime import datetime
from decimal import Decimal


class ProductSerializer(serializers.ModelSerializer):
    store_name = serializers.CharField(source='store.name', read_only=True) # 取得關聯的Store名稱
    class Meta:
        model = Product
        fields = ['id', 'description', 'name', 'price', 'stock', 'store_name']

    def validate_price(self, value): 
        if value < 0:
            raise serializers.ValidationError(
                "價格不能為負數"
            )   
        return value


class StoreSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True) # 取得關聯的產品列表
    class Meta:
        model = Store
        fields = [
            'merchant', 
            'name', 
            'description',
            'address', 
            'created_at',  
            'last_update',
            'products', 
        ] 
        read_only_fields = ["merchant", "created_at"] # 這些欄位為唯讀


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name') # 取得關聯的Product名稱
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2) # 取得關聯的Product價格
    class Meta:
        model = OrderItem
        fields = [
            'product_name',
            'product_price',
            'quantity',
            'item_subtotal'
        ] # 訂單項目小計

class OrderItemCreateSerializer(serializers.ModelSerializer):
        product = serializers.PrimaryKeyRelatedField(
            queryset=Product.objects.all()
        )
        class Meta:
            model = OrderItem
            fields = [
                'product', 
                'quantity', 
            ]

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'order_number',
            'member',
            'status',
            'payment_method',
            'receiver_name',
            'receiver_phone',
            'address',
            'note', 
            'items',
            'total_amount', 
        ]
        read_only_fields = [
            'order_number',
            'member',
            'status',
            'total_amount',
            'payment_method',
        ]
    order_number = serializers.CharField(read_only=True)
    items = OrderItemCreateSerializer(
        many=True, 
        write_only=True,
    )
         
    def create(self, validated_data):
        orderitem_data = validated_data.pop('items',[]) # 從validated_data中取出子資料(validated_data是DRF中已驗證過的dict資料)
        # member = validated_data.pop('member')

        if not orderitem_data:
            raise ValidationError("訂單至少要有一項商品喔！")

        with transaction.atomic():
            order = Order.objects.create(**validated_data) # 建立主資料訂單(子資料已經被取出，故可以create)

            total_amount = Decimal(0)

            for item in orderitem_data:
                product = Product.objects.select_for_update().get(
                    id=item['product'].id
                ) # 鎖定產品資料以避免競爭條件
                
                if product.stock < item['quantity']:
                    raise ValidationError(
                        f"{product.name} 庫存不足(剩餘 {product.stock} )"
                    )
                
                price = product.price
                subtotal = price * item['quantity']
                total_amount += subtotal
                
                product.stock -= item['quantity']
                product.save()

                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_purchase=price,
                ) # 一筆一筆建立子資料訂單，並連結到主資料訂單

            order.total_amount = total_amount
            order.save()

        return order # 回傳給前端主資料訂單(已經包含子資料訂單)
      

class OrderUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'receiver_name',
            'receiver_phone', 
            'address', 
            'note', 
            'status'
        ]

    def update(self, instance, validated_data):
        new_status = validated_data.get('status') 
        if new_status:
            if not instance.can_transition(new_status):
                raise ValidationError(
                    f"訂單無法從 {instance.status} 改為 {new_status} !"
                ) # 驗證訂單狀態的轉換正常
            instance.status = new_status
        
        instance.receiver_name = validated_data.get('receiver_name', instance.receiver_name)
        instance.receiver_phone = validated_data.get('receiver_phone', instance.receiver_phone)
        instance.address = validated_data.get('address', instance.address)
        instance.note = validated_data.get('note', instance.note)

        instance.save()
        return instance



class OrderSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(read_only=True) # 訂單編號
    member = serializers.IntegerField(source='member.id', read_only=True) 
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'member',
            'status', 
            'payment_method',
            'receiver_name',
            'receiver_phone',
            'address',
            'note',
            'created_at',  
            'items', 
            'total_amount',
            ]
        
class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True) # 產品列表
    count = serializers.IntegerField() # 總數量
    max_price = serializers.FloatField() # 最高價格

class OrderStatusBreakdownSerializer(serializers.Serializer):
    sratus = serializers.CharField()
    count = serializers.IntegerField()

class OrderSummarySerializer(serializers.Serializer):
    start = serializers.DateField(allow_null=True)
    end = serializers.DateField(allow_null=True)
    order_count = serializers.IntegerField()
    gmv = serializers.DecimalField(max_digits=12, decimal_places=2)
    aov = serializers.DecimalField(max_digits=12, decimal_places=2)