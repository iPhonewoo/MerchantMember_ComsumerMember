from django.urls import path
from member import views as member_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('register/', member_views.RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path("member/", member_views.MemberListCreateAPIView.as_view(), name="member_list_create"),
    path("member/<int:pk>/", member_views.MemberDetailAPIView.as_view(), name="member_detail"), 
]