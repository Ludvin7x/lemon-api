from rest_framework.permissions import BasePermission

class IsAuthenticatedBase(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return bool(user and user.is_authenticated and user.is_active)


class IsAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
        user = request.user
        return super().has_permission(request, view) and (user.is_staff or user.is_superuser)


class IsManagerOrAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
        user = request.user
        is_manager = user.groups.filter(name='Manager').exists()
        return super().has_permission(request, view) and (is_manager or user.is_staff or user.is_superuser)


class IsDeliveryCrewOrAdmin(IsAuthenticatedBase):
    def has_permission(self, request, view):
        user = request.user
        is_delivery = user.groups.filter(name='Delivery crew').exists()
        return super().has_permission(request, view) and (is_delivery or user.is_staff or user.is_superuser)
    
class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        is_customer = user.groups.filter(name='Customer').exists()
        return is_customer or user.is_staff or user.is_superuser