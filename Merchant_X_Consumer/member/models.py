from django.db import models
from datetime import datetime
# Create your models here.

class Member(models.Model):
    member_id = models.AutoField(primary_key=True)
    member_name = models.CharField(max_length=20)
    member_password = models.CharField(max_length=128)
    member_email = models.EmailField(max_length=200, unique=True)
    member_birth = models.DateField()
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
    merchant_id = models.AutoField(primary_key=True)
    merchant_name = models.CharField(max_length=20)
    merchant_password = models.CharField(max_length=128)
    merchant_email = models.EmailField(max_length=200, unique=True)
    merchant_birth = models.DateField()
    merchant_avatar = models.CharField(max_length=100, default='empty.png')
    last_update = models.DateTimeField(default=datetime.now())
    login_days = models.IntegerField(default=0)
    last_loginDate = models.DateTimeField(default=datetime.now())

    class Meta:
        db_table = 'merchant' # 指定資料表名稱

    def __str__(self):
        return self.merchant_name # 回傳物件的名稱