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
from rest_framework.permissions import IsAuthenticatedOrReadOnly # 確保只有已驗證的用戶可以存取這些API
from rest_framework.permissions import AllowAny  # 允許任何人存取這些API
from rest_framework.permissions import IsAdminUser  # 確保只有管理員用戶可以存取這些API
from rest_framework.permissions import IsAuthenticated  # 確保只有已驗證的用戶可以存取這些API
from rest_framework.response import Response
from rest_framework.views import APIView  # 基本的API視圖類別

from store.filter import (InStockFilterBackend, OrderFilter,  # 自定義的過濾器
                          ProductFilter)
from store.models import Store, Order, OrderItem, Product
from store.serializers import (StoreSerializer, OrderSerializer, ProductInfoSerializer,
                               ProductSerializer, OrderCreateSerializer)
from member.permissions import (IsMerchant, 
                                IsMember, 
                                IsOwnerOfStore, 
                                IsOwnerOfOrder, 
                                IsOwnerOfMemberProfile, 
                                IsOwnerOfProduct)
from rest_framework.exceptions import PermissionDenied # 用於權限拒絕例外
from datetime import datetime

# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    
    def get_permissions(self):
        if self.action == 'create':
           return [IsAuthenticated(), IsMerchant()] # 只有登入後的商家可以創建商店
        elif self.action in ['update', 'partial_update', 'destroy']:
           return [IsAuthenticated(), IsOwnerOfStore()] # 只有商店擁有者可以修改或刪除商店
        return [AllowAny()] # 任何人都可以查看商店列表和詳情
    
    def perform_create(self, serializer):
        user = self.request.user
        merchant = user.merchant
        
        existing_store = Store.objects.filter(merchant=merchant).first()
        if existing_store:
            raise PermissionDenied("每個商家只能擁有一個商店") # 確保商家只能有一個商店
        
        store = serializer.save(merchant=merchant) # 將商店與商家關聯起來並儲存
        return store
    
    def perform_update(self, serializer):
        serializer.save() # 儲存更新的商店資料

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action == 'create':
           return [IsAuthenticated(), IsMerchant()] # 只有登入後的商家可以新增、更新或刪除產品
        elif self.action in ['update', 'partial_update', 'destroy']:
           return [IsAuthenticated(), IsOwnerOfProduct()]
        return [AllowAny()] # 任何人都可以查看產品列表和詳情
    
    def perform_create(self, serializer):
        user = self.request.user
        merchant = user.merchant
        
        try:
            store = Store.objects.get(merchant=merchant)
        except Store.DoesNotExist:
            raise PermissionDenied("您尚未創建商店哦！") # 確保商戶有商店
        
        product = serializer.save(store=store) # 將產品與商店關聯起來並儲存

        return product
    
    def perform_update(self, serializer):
        serializer.save() # 儲存更新的產品資料

    
class orderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product') # 預先取得相關的OrderItem和Product以優化查詢
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly] # 只有會員可以存取這些API
    filterset_class = OrderFilter # 使用OrderFilter進行篩選
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
    ] #  使用多種過濾後端

    def perform_create(self, serializer):
        serializer.save(member=self.request.user.member) # 在建立訂單時自動設定user欄位為當前用戶

    def get_serializer_class(self):
        # can also check if POST: if self.request.method == 'POST'
        if self.action == 'create' or self.action == 'update':
            return OrderCreateSerializer # 使用OrderCreateSerializer來建立訂單
        return super().get_serializer_class() # 使用預設的序列化器

    def get_queryset(self):
        qs = super().get_queryset() # 獲取預設的查詢集
        if not self.request.user.is_authenticated:
            return Order.objects.none()
        elif self.request.user.role == 'member':
            qs = qs.filter(member=self.request.user.member) # 會員只能看到自己的訂單
            return qs
        elif self.request.user.role == 'merchant':
            try:
                store = Store.objects.get(user=self.request.user)
            except Store.DoesNotExist:
                return Order.objects.none() # 商家無商店無法查看訂單
            
            qs = qs.filter(items__product__store=store).distinct() # 商家只能看到包含自己產品的訂單
            return qs
        else:
            return qs # 管理員可以看到所有訂單

    
    @action(
        detail=False, 
        methods=['get'], 
        url_path='user-orders', # 自訂URL路徑
        permission_classes=[IsAuthenticated] # 只有已驗證的用戶可以存取這些API
    )
    def user_orders(self, request):
        orders = self.get_queryset().filter(user=request.user.member) # 只顯示該用戶的訂單
        serializer = self.get_serializer(orders, many=True) # 序列化訂單資料
        return Response(serializer.data) # 回傳序列化後的資料 


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products, # 所有產品資料
            'count': len(products), # 取得產品總數量
            'max_price': products.aggregate(max_price=Max('price'))['max_price'] # 取得最高價格
        })
        return Response(serializer.data)


