from django.db.models import Max  # 用於聚合查詢
from django.shortcuts import get_object_or_404  # 用於取得物件或回傳404錯誤
from django_filters.rest_framework import \
    DjangoFilterBackend  # 使用Django Filter進行過濾
from rest_framework import viewsets  # 此功能可包含所有CRUD且自動處理路由
from rest_framework.decorators import action  # 用於在ViewSet中定義自訂動作
from rest_framework import (filters,  # 使用Django REST framework的通用視圖和過濾器
                            generics)
from rest_framework.decorators import \
    api_view  # 使用Django REST framework的api_view裝飾器
from rest_framework.pagination import (LimitOffsetPagination,  # 分頁類別
                                       PageNumberPagination)
from rest_framework.permissions import AllowAny  # 允許任何人存取這些API
from rest_framework.permissions import IsAdminUser  # 確保只有管理員用戶可以存取這些API
from rest_framework.permissions import IsAuthenticated  # 確保只有已驗證的用戶可以存取這些API
from rest_framework.response import Response
from rest_framework.views import APIView  # 基本的API視圖類別

from store.filter import (InStockFilterBackend, OrderFilter,  # 自定義的過濾器
                          ProductFilter)
from store.models import Order, OrderItem, Product
from store.serializers import (OrderSerializer, ProductInfoSerializer,
                               ProductSerializer, OrderCreateSerializer)

# Create your views here.

class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by('pk') # 取得所有產品
    serializer_class = ProductSerializer # 使用ProductSerializer將Product物件轉換成JSON格式
    filterset_class = ProductFilter # 使用ProductFilter進行篩選
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
        InStockFilterBackend
    ] #  使用多種過濾後端
    search_fields = ['name', 'description'] # 允許根據名稱和描述進行搜尋
    ordering_fields = ['name', 'price', 'stock'] # 允許根據價格和庫存進行排序
    pagination_class = PageNumberPagination # 使用分頁功能
    pagination_class.page_size = 2 # 每頁顯示兩個產品
    pagination_class.page_size_query_param = 'size' # 允許客戶端指定每頁顯示的產品數量
    pagination_class.max_page_size = 4 # 每頁最多顯示十個產品

    def get_permissions(self):
        self.permission_classes = [AllowAny] # 任何人都可以查看產品列表
        if self.request.method == 'POST':
            self.permission_classes = [IsAdminUser] # 只有管理員用戶可以新增產品
        return super().get_permissions()

class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all() # 取得所有產品
    serializer_class = ProductSerializer # 使用ProductSerializer將Product物件轉換成JSON格式

    def get_permissions(self):
        self.permission_classes = [AllowAny] # 任何人都可以查看產品詳情
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser] # 只有管理員用戶可以更新或刪除產品
        return super().get_permissions()

class orderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product') # 預先取得相關的OrderItem和Product以優化查詢
    serializer_class = OrderSerializer
    permission_classes = [AllowAny] # 任何人都可以存取這些API
    filterset_class = OrderFilter # 使用OrderFilter進行篩選
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
    ] #  使用多種過濾後端

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) # 在建立訂單時自動設定user欄位為當前用戶

    def get_serializer_class(self):
        # can also check if POST: if self.request.method == 'POST'
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer # 使用OrderCreateSerializer來建立訂單
        return super().get_serializer_class() # 使用預設的序列化器

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user) # 非管理員用戶只能看到自己的訂單
        return qs
    
    @action(
        detail=False, 
        methods=['get'], 
        url_path='user-orders', # 自訂URL路徑
        permission_classes=[IsAuthenticated] # 只有已驗證的用戶可以存取這些API
    )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user) # 只顯示該用戶的訂單
        serializer = self.get_serializer(orders, many=True)



# class OrderListAPIView(generics.ListAPIView):
#     queryset = orders = Order.objects.all() # 取得所有訂單
#     serializer_class = OrderSerializer 

# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = orders = Order.objects.all()
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated] # 只有已驗證的用戶可以存取這些API
#     def get_queryset(self):
#         qs = super().get_queryset() 
#         return qs.filter(user=self.request.user) # 只顯示該用戶的訂單

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products, # 所有產品資料
            'count': len(products), # 取得產品總數量
            'max_price': products.aggregate(max_price=Max('price'))['max_price'] # 取得最高價格
        })
        return Response(serializer.data)


