from django.urls import path
from store import views as store_views
from rest_framework.routers import DefaultRouter # 使用Django REST framework的路由系統



urlpatterns = [
    path("products/", store_views.ProductListCreateAPIView.as_view(), name="product_list_create"), 
    path("products/<int:pk>/", store_views.ProductDetailAPIView.as_view(), name="product_detail"), 
    path("products/info/", store_views.ProductInfoAPIView.as_view(), name="product_info"),
    path("stores/<int:pk>/", store_views.StoreDetailAPIView.as_view(), name="store_detail"),
    # path("orders/", store_views.OrderListAPIView.as_view(), name="order_list"),
    # path("user-orders/", store_views.UserOrderListAPIView.as_view(), name="user-orders"),
    
]

router = DefaultRouter()
router.register('orders', store_views.orderViewSet, basename='order') # 註冊Order的ViewSet到路由系統
urlpatterns += router.urls