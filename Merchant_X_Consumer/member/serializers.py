from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer # 用於JWT驗證
from django.db import transaction # 用於資料庫交易管理
from rest_framework import serializers
from member.models import User, Member, Merchant
from store.models import Store,Order, OrderItem
from store.serializers import OrderSerializer
from datetime import datetime

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=2) # 密碼不會回傳時露出來，且長度至少為2

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'role')

    def validatepassword(self, value): 
        # validate_password(value) # 使用Django內建的密碼驗證器
        if len(value) < 2:
            raise serializers.ValidationError(
                "密碼長度至少需要2個字元"
            )   
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, role=role) # 建立使用者物件
        user.set_password(password) # 設定加密後的密碼
        user.save()

        if role == 'merchant':
            merchant = Merchant.objects.create(user=user)
            store = Store.objects.create(merchant=merchant, name=f"{user.username}的商店", address="", description="")
        else:
            Member.objects.create(user=user)
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user) # 獲取預設的token
        token['role'] = user.role # 加入使用者角色到token中
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs) # 獲取預設的驗證資料
        self.user.last_login=datetime.now() # 更新最後登入時間
        if self.user.role == 'member':
            # 如果是會員，更新會員的登入天數和點數
            if hasattr(self.user, 'member'):
                member = self.user.member
                now = datetime.now().date()
                thelast = member.last_loginDate.date()
                day_passed = (now - thelast).days
                if day_passed > 0 or member.login_days == 0:
                    member.login_days += 1
                    if member.login_days % 2 == 0:
                        member.member_points += 5 # 每兩天登入增加5點
                member.last_loginDate = datetime.now()
                member.save()
        self.user.save()
        data['username'] = self.user.username # 回傳使用者名稱
        data['role'] = self.user.role # 回傳使用者角色
        return data
    
    
class MemberSerializer(serializers.ModelSerializer):
    orders = OrderSerializer(many=True, read_only=True) # 取得關聯的訂單列表
    class Meta:
        model = Member
        fields = [
            'member_id',
            'member_name',
            'member_email',
            'member_birth',
            'member_avatar',
            'orders',
            'last_update',
            'member_points',
            'login_days',
            'last_loginDate'
        ] # 指定要序列化的欄位

    

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = [
            'merchant_id',
            'merchant_name',
            'merchant_email',
            'merchant_birth',
            'merchant_avatar',
            'last_update',
            'login_days',
            'last_loginDate'
        ] # 指定要序列化的欄位