import uuid
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.conf import settings



# Create your models here.

# class User(AbstractUser):
    # pass
    # user_id = models.AutoField(primary_key=True)
    # user_name = models.CharField(max_length=20)
    # user_email = models.EmailField(max_length=200, unique=True)
    # user_type = models.CharField(max_length=10)  # 'member' 或 'merchant'
    # date_joined = models.DateTimeField(default=datetime.now())
    # is_active = models.BooleanField(default=True)

    # USERNAME_FIELD = 'user_email'
    # REQUIRED_FIELDS = ['user_name', 'user_type']

    # class Meta:
    #     db_table = 'user'  # 指定資料表名稱

    # def __str__(self):
    #     return self.user_name  # 回傳物件的名稱

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    @property
    def in_stock(self):
        return self.stock > 0
    
    def __str__(self):
        return self.name

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        CANCELED = 'Canceled'

    order_id = models.AutoField(primary_key=True)
    user = models.ForeignKey('member.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    

    def __str__(self):
        return f"Order {self.order_id} by {self.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items', # 讓Order可以透過items屬性存取相關的OrderItem
        )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.order_id}"