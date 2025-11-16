from django.db import transaction # 用於資料庫交易管理
from rest_framework import serializers
from member.models import Member, Merchant

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = [
            'member_id',
            'member_name',
            'member_email',
            'member_birth',
            'member_avatar',
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