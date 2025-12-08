from django.urls import path
from store import views as store_views
from rest_framework.routers import DefaultRouter # 使用Django REST framework的路由系統



urlpatterns = [
    path("products/info/", store_views.ProductInfoAPIView.as_view(), name="product_info"),
    path("orders/", store_views.OrderCreateAPIView.as_view(), name="order_list"),
    path("orders/<int:pk>/", store_views.OrderDetailAPIView.as_view(), name="order_detail"),
    # path("user-orders/", store_views.UserOrderListAPIView.as_view(), name="user-orders"),   
]

router = DefaultRouter()
router.register('stores', store_views.StoreViewSet, basename='store') # 註冊Store的ViewSet到路由系統
router.register('products', store_views.ProductViewSet, basename='product') # 註冊Product的ViewSet到路由系統
urlpatterns += router.urls