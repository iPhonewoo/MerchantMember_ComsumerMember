import uuid
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from member.models import User, Member, Merchant


# Create your models here.
class Store(models.Model):
    merchant = models.OneToOneField(
        Merchant, 
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(default=datetime.now())
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name  # 回傳物件的名稱


class Product(models.Model):
    store = models.ForeignKey(
        Store, 
        on_delete=models.CASCADE, 
        related_name='products' # 讓Store可以透過products屬性存取相關的Product
    )
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    stock = models.PositiveIntegerField()
    
    @property
    def in_stock(self):
        return self.stock > 0
    
    def __str__(self):
        return self.name
    

class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        SHIPPED = 'shipped', 'Shipped'
        COMPLETED = 'completed', 'Completed'
        CANCELED = 'canceled', 'Canceled'
            
    member = models.ForeignKey(
        Member, 
        on_delete=models.CASCADE,
        related_name='orders'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    
    def can_transition(self, new_status):
        transitions = {
            self.StatusChoices.PENDING: [self.StatusChoices.PAID, self.StatusChoices.CANCELED],
            self.StatusChoices.PAID: [self.StatusChoices.SHIPPED],
            self.StatusChoices.SHIPPED: [self.StatusChoices.COMPLETED],
            self.StatusChoices.COMPLETED: [],
            self.StatusChoices.CANCELED: [],
        }
        return new_status in transitions[self.status, []] # 避免有非預期狀態而導致API崩潰

    def __str__(self):
        return f"Order {self.id} by {self.member.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE,
        related_name='items', # 讓Order可以透過items屬性存取相關的OrderItem
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)

    @property
    def item_subtotal(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"