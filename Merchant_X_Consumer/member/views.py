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
from member.serializers import RegisterSerializer, MemberSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics
from rest_framework.permissions import AllowAny  # 允許任何人存取這些API
from rest_framework.permissions import IsAdminUser  # 確保只有管理員用戶可以存取這些API
from rest_framework.permissions import IsAuthenticated  # 確保只有已驗證的用戶可以存取這些API

# Create your views here.

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    

class MemberListCreateAPIView(generics.ListCreateAPIView):
    queryset = Member.objects.order_by('pk') # 取得所有產品
    serializer_class = MemberSerializer
    
    def member_points(self, obj):
        if self.request.method == 'POST':
            obj.member_points = 100 # 新增會員時初始點數為100
        if obj.login_days % 2 == 0 and obj.login_days != 0:
            obj.member_points += 5 # 每兩天登入增加5點
        return obj.member_points

class MemberDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Member.objects.all() # 取得所有產品
    serializer_class = MemberSerializer # 使用ProductSerializer將Product物件轉換成JSON格式

    def get_permissions(self):
        self.permission_classes = [AllowAny] # 任何人都可以查看產品詳情
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAdminUser] # 只有管理員用戶可以更新或刪除產品
        return super().get_permissions()