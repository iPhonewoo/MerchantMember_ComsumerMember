from django.urls import path
from store import views as store_views
from rest_framework.routers import DefaultRouter # 使用Django REST framework的路由系統



urlpatterns = [
    path("products/info/", store_views.ProductInfoAPIView.as_view(), name="product_info"),
    path("orders/", store_views.OrderListCreateAPIView.as_view(), name="order_list_create"),
    path("orders/<int:pk>/", store_views.OrderDetailAPIView.as_view(), name="order_detail"),
    path("orders/<int:pk>/pay/", store_views.OrderPayAPIView.as_view(), name="order_pay"),
    path("orders/<int:pk>/ship/", store_views.OrderShipAPIView.as_view(), name="order_ship"),
    path("orders/<int:pk>/cancel/", store_views.OrderCancelAPIView.as_view(), name="order_cancel"),

]

router = DefaultRouter()
router.register('stores', store_views.StoreViewSet, basename='store') # 註冊Store的ViewSet到路由系統
router.register('products', store_views.ProductViewSet, basename='product') # 註冊Product的ViewSet到路由系統
urlpatterns += router.urls