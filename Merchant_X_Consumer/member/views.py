# 匯入 member 資料庫
from django.shortcuts import render, redirect
from member.models import User, Member 
# 匯入加密及驗證密碼的功能
from django.contrib.auth.hashers import make_password, check_password
# 找到檔案上傳的路徑
from django.core.files.storage import FileSystemStorage
# 匯入序列化功能
# from django.core import serializers
from datetime import datetime
from member.serializers import RegisterSerializer, MemberSerializer, MyTokenObtainPairSerializer
from rest_framework import generics
from rest_framework import mixins, viewsets
from rest_framework.permissions import AllowAny  # 允許任何人存取這些API
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAdminUser  # 確保只有管理員用戶可以存取這些API
from rest_framework.permissions import IsAuthenticated  # 確保只有已驗證的用戶可以存取這些API
from rest_framework_simplejwt.views import TokenObtainPairView # 用於JWT驗證
from member.permissions import IsMember, IsOwnerOfMemberProfile, IsAdmin
from rest_framework.exceptions import PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # 允許任何人存取註冊API

@method_decorator(csrf_exempt, name="dispatch")
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print("🔥 LOGIN POST HIT 🔥")
        return super().post(request, *args, **kwargs)


class MemberViewSet(
    mixins.RetrieveModelMixin, 
    mixins.UpdateModelMixin, 
    viewsets.GenericViewSet
):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer

    def get_permissions(self):
        return [IsAuthenticated(), IsOwnerOfMemberProfile()]
    
    def perform_update(self, serializer):
        serializer.save()