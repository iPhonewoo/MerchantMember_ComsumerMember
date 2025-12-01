from django.urls import path
from member import views as member_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('register/', member_views.RegisterView.as_view(), name='register'),
    path('login/', member_views.MyTokenObtainPairView.as_view(), name='login'), # JWT 登入
    path('login/refresh/', TokenRefreshView.as_view(), name='refresh'), # JWT 重新整理Token
    path('members/', member_views.MemberListCreateAPIView.as_view(), name='member_list_create'),
    path('members/<int:pk>/', member_views.MemberDetailAPIView.as_view(), name='member_detail'),
    # path("member/", member_views.MemberListCreateAPIView.as_view(), name="member_list_create"),
    # path("member/<int:pk>/", member_views.MemberDetailAPIView.as_view(), name="member_detail"), 
]