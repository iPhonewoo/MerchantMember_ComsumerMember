from django.db.models import Max  # 用於聚合查詢
from django.shortcuts import get_object_or_404  # 用於取得物件或回傳404錯誤
from django_filters.rest_framework import \
    DjangoFilterBackend  # 使用Django Filter進行過濾
from rest_framework.decorators import action  # 用於在ViewSet中定義自訂動作
from rest_framework import (filters,  # 使用Django REST framework的通用視圖和過濾器
                            generics,
                            status,
                            viewsets)
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
from member.models import Merchant
from store.serializers import (StoreSerializer, OrderSerializer, ProductInfoSerializer,
                               ProductSerializer, OrderCreateSerializer, OrderUpdateSerializer,
                               OrderSummarySerializer)
from store.services.order_analytics import build_order_summary
from member.permissions import (IsMerchant, 
                                IsMember, 
                                IsOwnerOfStore, 
                                IsOwnerOfOrder, 
                                IsOwnerOfMemberProfile, 
                                IsOwnerOfProduct)
from rest_framework.exceptions import ValidationError, PermissionDenied # 用於權限拒絕例外
from datetime import datetime

# Create your views here.
def parse_date(value):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()

class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination_class = PageNumberPagination
    
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


class OrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related('items__product')

    def get_permissions(self):
        if self.request.method == 'POST':
            return[IsAuthenticated(), IsMember()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer
    
    # def perform_create(self, serializer):
        # serializer.save(member=self.request.user.member)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            # 🔥 關鍵：把真正的錯誤印出來
            print("SERIALIZER ERRORS =", serializer.errors)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(member=request.user.member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user =self.request.user

        if not user.is_authenticated:
            return Order.objects.none()
        
        if user.role == 'member':
            return Order.objects.filter(member=user.member).prefetch_related('items__product')
        
        if user.role == 'merchant':
            try:
                store = user.merchant.store
                return Order.objects.filter(
                    item__product__store=store
                ).distinct().prefetch_related('items__product')
            except Store.DoesNotExist:
                return Order.objects.none()
            
        return Order.objects.all().prefetch_related('items__product')
    

class OrderDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.prefetch_related('items__product')
    serializer_class = OrderSerializer
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsAuthenticated(), IsOwnerOfOrder()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return OrderUpdateSerializer
        return OrderSerializer
    
    def perform_update(self, serializer):
        serializer.save()

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            return Order.objects.none()
        
        if user.role == 'member':
            return Order.objects.filter(member=user.member) # 會員只會看到自己的訂單
        
        if user.role == 'merchant':
            try:
                store = user.merchant.store
                return Order.objects.filter(
                    items__product__store=store
                ).distinct() #商家只能看到有自己商品的訂單
            except Store.DoesNotExist:
                return Order.objects.none() # 商家無商店無法查看訂單
            
        return Order.objects.all() # 管理員可以看到所有訂單


class OrderPayAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfOrder]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        new_status = Order.StatusChoices.PAID

        if not order.can_transition(new_status):
            raise ValidationError(
                f"訂單無法從 {order.status} 改為 {new_status} !"
            )
        
        order.status = new_status
        order.payment_method = request.data.get(
            'payment_method', Order.PaymentMethodChoices.UNPAID
        ) 
        order.paid_at = datetime.now()
        order.save()

        return Response(
            {"detail": "付款成功", "status": order.status},
            status=status.HTTP_200_OK
        )


class OrderShipAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)

        try:
            store = request.user.merchant.store
        except Store.DoesNotExist:
            raise PermissionDenied("您尚未創建商店哦！")
        
        has_own_product = Order.objects.filter(
            pk=pk,
            items__product__store=store
        ).exists()

        if not has_own_product:
            raise PermissionDenied("此單並無您商店的商品，無法出貨！")

        new_status =Order.StatusChoices.SHIPPED

        if not order.can_transition(new_status):
            raise ValidationError(
                f"訂單無法從 {order.status} 改為 {new_status} !"
            )
        
        order.status = new_status
        order.save()

        return Response(
            {"detail": "出貨成功", "status": order.status},
            status=status.HTTP_200_OK
        )


class OrderCancelAPIView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOfOrder]

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        self.check_object_permissions(request, order)

        new_status = Order.StatusChoices.CANCELED

        if not order.can_transition(new_status):
            raise ValidationError(
                f"訂單無法從 {order.status} 改為 {new_status} !"
            )
        
        order.status = new_status
        order.save()

        return Response(
            {"detail": "訂單已取消", "status": order.status},
            status=status.HTTP_200_OK
        )

class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer({
            'products': products, # 所有產品資料
            'count': len(products), # 取得產品總數量
            'max_price': products.aggregate(max_price=Max('price'))['max_price'] # 取得最高價格
        })
        return Response(serializer.data)
    
class OrderAnalyticsSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated, IsMerchant]

    def get(self, request):
        try:
            merchant = Merchant.objects.get(user=request.user)
        except Merchant.DoesNotExist:
            raise PermissionDenied("您不是此商品訂單的商家，無法查看這些訂單的分析資料！")

        start = parse_date(request.query_params.get("start"))
        end = parse_date(request.query_params.get("end"))

        summary = build_order_summary(
            merchant=merchant,
            start=start,
            end=end,
        )

        serializer = OrderSummarySerializer(summary)
        return Response(serializer.data)

