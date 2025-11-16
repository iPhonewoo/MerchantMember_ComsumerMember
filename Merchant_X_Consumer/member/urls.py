from django.urls import path
from member import views as member_views

urlpatterns = [
    path("member/", member_views.MemberListCreateAPIView.as_view(), name="member_list_create"),
    path("member/<int:pk>/", member_views.MemberDetailAPIView.as_view(), name="member_detail"), 
]