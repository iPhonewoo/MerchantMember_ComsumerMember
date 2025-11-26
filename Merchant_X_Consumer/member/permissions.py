from rest_framework.permissions import BasePermission

class IsMerchant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "merchant"

    def has_object_permission(self, request, view, obj):
        # 商家只能操作自己的 商店 或 商品
        if hasattr(obj, 'user'): # Store
            return obj.user == request.user
        if hasattr(obj, 'store'): # Product
            return obj.store.user == request.user
        return False
    
class IsMember(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "member"

    def has_object_permission(self, request, view, obj):
        # 會員只能操作自己的 會員資料
        if hasattr(obj, 'user'): # Member
            return obj.user == request.user
        return False