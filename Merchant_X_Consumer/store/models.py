import random
from decimal import Decimal
from django.db import models
from datetime import datetime
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from member.models import User, Member, Merchant


# Create your models here.
def generate_order_number():
    today = datetime.now().strftime('%Y%m%d')
    random_digits = str(random.randint(100000, 999999))
    return f"ORD{today}-{random_digits}"

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
    order_number = models.CharField(max_length=30, unique=True, editable=False)
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
    receiver_name = models.CharField(max_length=50)
    receiver_phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )

    products = models.ManyToManyField(Product, through='OrderItem', related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class PaymentMethodChoices(models.TextChoices):
        UNPAID = 'unpaid', 'Unpaid'
        CREDIT_CARD = 'credit_card', 'Credit Card'
        LINE_PAY = 'line_pay', 'LINE Pay'
        CASH = 'cash', 'Cash'
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethodChoices.choices,
        default=PaymentMethodChoices.UNPAID
    )
    transaction_id = models.CharField(max_length=64, null=True, blank=True) # 金流交易編號（只有已付款訂單才會有）
    paid_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            new_order_number = generate_order_number()
            while Order.objects.filter(order_number=new_order_number).exists():
                new_order_number = generate_order_number()
            self.order_number = new_order_number

        super().save(*args, **kwargs)
     
    def can_transition(self, new_status):
        transitions = {
            'pending': ['paid', 'canceled'],
            'paid': ['shipped'],
            'shipped': ['completed'],
            'completed': [],
            'canceled': [],
        }
        return new_status in transitions.get(self.status, []) # 避免非預期狀態而崩潰，故給空集合

    def __str__(self):
        return f"Order {self.order_number} by {self.member.user.username}"
    

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
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def item_subtotal(self):
        return self.price_at_purchase * Decimal(self.quantity)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} @ {self.price_at_purchase} in Order {self.order.id}"