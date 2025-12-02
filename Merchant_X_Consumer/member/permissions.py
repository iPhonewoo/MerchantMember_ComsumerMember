from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return(
            request.user.is_authenticated and
            hasattr(request.user, "role") and 
            request.user.role == 'admin'
        )


class IsMerchant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "role") and # 防止 AnonymousUser 錯誤
            request.user.role == "merchant"
        )


class IsOwnerOfStore(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj 是 Store instance
        return (
            request.user.is_authenticated and
            hasattr(request.user, "merchant") and 
            obj.merchant == request.user.merchant
        )

class IsOwnerOfProduct(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "merchant") and
            obj.store.merchant == request.user.merchant
        )

class IsMember(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            hasattr(request.user, "role") and 
            request.user.role == "member"
        )


class IsOwnerOfMemberProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj 是 Member instance
        return (
            request.user.is_authenticated and
            hasattr(request.user, "member") and
            obj.user == request.user
        )


class IsOwnerOfOrder(BasePermission):
    def has_object_permission(self, request, view, obj):
        # obj 是 Order instance
        return (
            request.user.is_authenticated and
            hasattr(request.user, "member") and
            obj.member == request.user.member
        )
    