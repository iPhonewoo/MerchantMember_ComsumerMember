from django.db import transaction # 用於資料庫交易管理
from rest_framework import serializers
from store.models import Product, Order, OrderItem


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['description', 'name', 'price', 'stock']

    def validate_price(self, value): 
        if value < 0:
            raise serializers.ValidationError(
                "價格不能為負數"
            )   
        return value 
    
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

class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = [
                'product', 
                'quantity', 
            ]
    order_id = serializers.CharField(read_only=True)
    items = OrderItemCreateSerializer(many=True, required=False) # 嵌套的OrderItem序列化器，用於建立訂單時使用

    
    def update(self, instance, validated_data):
        orderitem_data = validated_data.pop('items') # 從validated_data中取出子資料(validated_data是DRF中已驗證過的dict資料)

        with transaction.atomic(): # 使用資料庫交易確保資料一致性
            order = super().update(instance, validated_data) # 更新主資料訂單(子資料已經被取出，故可以update)

            if orderitem_data is not None:
                order.items.all().delete() # 刪除舊的OrderItem

                for item in orderitem_data:
                    OrderItem.objects.create(order=order, **item) # 一筆一筆建立子資料訂單，並連結到主資料訂單
            return order # 回傳給前端主資料訂單(已經包含子資料訂單)
            

    def create(self, validated_data):
        orderitem_data = validated_data.pop('items') # 從validated_data中取出子資料(validated_data是DRF中已驗證過的dict資料)
        order = Order.objects.create(**validated_data) # 建立主資料訂單(子資料已經被取出，故可以create)

        for item in orderitem_data:
            OrderItem.objects.create(order=order, **item) # 一筆一筆建立子資料訂單，並連結到主資料訂單

        return order # 回傳給前端主資料訂單(已經包含子資料訂單)
    
    class Meta:
        model = Order
        fields = [
            'order_id',
            'user', 
            'status', 
            'items', 
        ]
        extra_kwargs = {
            'user': {'read_only': True}, # user欄位為唯讀
        }
    
class OrderSerializer(serializers.ModelSerializer):
    order_id = serializers.CharField(read_only=True) # 訂單ID為唯讀 
    items = OrderItemSerializer(many=True)
    total_price =serializers.SerializerMethodField(method_name='get_total_price') # 計算訂單總價
    def get_total_price(self, obj):
        return sum(item.item_subtotal for item in obj.items.all()) # 計算訂單總價

    class Meta:
        model = Order
        fields = [
            'order_id', 
            'user', 
            'created_at', 
            'status', 
            'items', 
            'total_price',
            ]
        
class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True) # 產品列表
    count = serializers.IntegerField() # 總數量
    max_price = serializers.FloatField() # 最高價格