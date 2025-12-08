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
    filterset_class = ProductFilter 
    filter_backends = [
        DjangoFilterBackend, 
        filters.SearchFilter,
        filters.OrderingFilter,
    ] #  使用多種過濾後端

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


class OrderCreateAPIView(generics.CreateAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated, IsMember]

    def perform_create(self, serializer):
        serializer.save(member=self.request.user.member)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    

class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwnerOfOrder()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderCreateSerializer
        return OrderSerializer
    
    def perform_update(self, serializer):
        serializer.save(member=self.request.user.member)

    def perform_destroy(self, instance):
        instance.delete()

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset() # 獲取預設的查詢集
        if not user.is_authenticated:
            return Order.objects.none()
        elif user.role == 'member':
            qs = qs.filter(member=user.member) # 會員只能看到自己的訂單
            return qs
        elif user.role == 'merchant':
            try:
                store = Store.objects.get(user=user)
            except Store.DoesNotExist:
                return Order.objects.none() # 商家無商店無法查看訂單
            
            qs = qs.filter(items__product__store=store).distinct() # 商家只能看到包含自己產品的訂單
            return qs
        else:
            return qs # 管理員可以看到所有訂單


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products, # 所有產品資料
            'count': len(products), # 取得產品總數量
            'max_price': products.aggregate(max_price=Max('price'))['max_price'] # 取得最高價格
        })
        return Response(serializer.data)


