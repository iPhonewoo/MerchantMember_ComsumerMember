from django.contrib import admin
from store.models import Order, OrderItem
from member.models import User

# Register your models here.

class OrderItemInline(admin.TabularInline): 
    model = OrderItem # allows editing of OrderItems inline within the Order admin interface
    

class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline, # allows editing of OrderItems within the Order admin interface
    ]

admin.site.register(Order, OrderAdmin) # Register the Order model with the custom OrderAdmin class
admin.site.register(User) # Register the User model to manage users in the admin interface

# from django.contrib import admin
# from django.db import transaction
# from store.models import Order, OrderItem


# class OrderItemInline(admin.TabularInline):
#     model = OrderItem
#     extra = 1  # 顯示一個空白輸入欄
#     min_num = 0


# @admin.register(Order)
# class OrderAdmin(admin.ModelAdmin):
#     inlines = [OrderItemInline]
#     list_display = ('order_id', 'user', 'status', 'created_at')
#     list_filter = ('status', 'created_at')
#     search_fields = ('user__username', 'order_id')

#     # 🔧 關鍵修改：覆寫 save_related
#     def save_related(self, request, form, formsets, change):
#         """
#         這段確保 Order 一定會先被儲存進資料庫，
#         再處理它的 inline（OrderItem）關聯。
#         """
#         with transaction.atomic():
#             form.save()  # 儲存主表（Order）
#             super().save_related(request, form, formsets, change)