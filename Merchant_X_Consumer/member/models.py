from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from datetime import datetime
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('merchant', 'Merchant'),
        ('member', 'Member'),
        ('admin', 'Admin'),
    )
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES,
        default='member'
    )


class Member(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
    )
    name = models.CharField(max_length=20)
    birthday = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    phone_num = models.CharField(max_length=20, null=True, blank=True)
    member_avatar = models.CharField(
        max_length=100, 
        default='empty.png'
    )
    last_update = models.DateTimeField(auto_now=True)
    member_points = models.IntegerField(default=50)
    login_days = models.IntegerField(default=0)
    last_loginDate = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'member' # 指定資料表名稱

    def __str__(self):
        return self.name # 回傳物件的名稱


class Merchant(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE
    ) 

    class Meta:
        db_table = 'merchant' # 指定資料表名稱

    def __str__(self):
        return self.user.username # 回傳物件的名稱