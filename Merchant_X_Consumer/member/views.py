from django.shortcuts import render, redirect
# 匯入 member 資料庫
from member.models import User, Member
# 匯入加密及驗證密碼的功能
from django.contrib.auth.hashers import make_password, check_password
# 找到檔案上傳的路徑
from django.core.files.storage import FileSystemStorage
# 匯入序列化功能
# from django.core import serializers
from datetime import datetime
# serializer 測試
from django.shortcuts import get_object_or_404 
from django.http import JsonResponse
from member.serializers import RegisterSerializer, MemberSerializer, MyTokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.permissions import AllowAny  # 允許任何人存取這些API
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.permissions import IsAdminUser  # 確保只有管理員用戶可以存取這些API
from rest_framework.permissions import IsAuthenticated  # 確保只有已驗證的用戶可以存取這些API
from rest_framework_simplejwt.views import TokenObtainPairView # 用於JWT驗證
from member.permissions import IsMember
from rest_framework.exceptions import PermissionDenied
# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]  # 允許任何人存取註冊API


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
    
class MemberListCreateAPIView(generics.ListCreateAPIView):
    queryset = Member.objects.order_by('pk') # 取得所有產品
    serializer_class = MemberSerializer
    

class MemberDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MemberSerializer # 使用ProductSerializer將Product物件轉換成JSON格式

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
              return [IsMember()] # 只有會員可以更新或刪除會員資料
        return [AllowAny()] # 其他人只能查看會員資料
    
    def get_queryset(self):
        if self.request.method == 'GET':
            return Member.objects.all() # 任何人都可以查看會員資料
        return Member.objects.filter(user=self.request.user) # 會員只能查看自己的會員資料
    
    def perform_update(self, serializer):
        user = serializer.save() # 儲存更新的會員資料
        user.last_update=datetime.now() # 更新最後修改時間
        user.save() 