from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from datetime import datetime
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('merchant', 'Merchant'),
        ('member', 'Member'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


class Member(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    member_id = models.AutoField(primary_key=True)
    member_name = models.CharField(max_length=20)
    member_password = models.CharField(max_length=128)
    member_email = models.EmailField(max_length=200, unique=True)
    member_birth = models.DateField(null=True, blank=True)
    member_avatar = models.CharField(max_length=100, default='empty.png')
    last_update = models.DateTimeField(default=datetime.now(), editable=False)
    member_points = models.IntegerField(default=0, editable=False)
    login_days = models.IntegerField(default=0, editable=False)
    last_loginDate = models.DateTimeField(default=datetime.now(), editable=False)

    class Meta:
        db_table = 'member' # 指定資料表名稱

    def __str__(self):
        return self.member_name # 回傳物件的名稱


class Merchant(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    store_name = models.CharField(max_length=100, null=True, blank=True)
    merchant_password = models.CharField(max_length=128)
    merchant_email = models.EmailField(max_length=200, unique=True)
    merchant_birth = models.DateField()
    merchant_avatar = models.CharField(max_length=100, default='empty.png')
    last_update = models.DateTimeField(default=datetime.now(), editable=False)
    login_days = models.IntegerField(default=0, editable=False)
    last_loginDate = models.DateTimeField(default=datetime.now(), editable=False)

    class Meta:
        db_table = 'merchant' # 指定資料表名稱

    def __str__(self):
        return self.store_name # 回傳物件的名稱