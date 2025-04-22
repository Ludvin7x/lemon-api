from rest_framework.permissions import BasePermission

class IsUserInGroup(BasePermission):
    """
    Permiso base para verificar si el usuario está en uno de los grupos especificados.
    """
    def has_permission(self, request, view, groups):
        return request.user.is_authenticated and request.user.groups.filter(name__in=groups).exists()

class IsDeliveryCrew(IsUserInGroup):
    """
    Permiso personalizado para permitir acceso solo a los miembros del grupo 'Delivery crew'.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view, groups=['Delivery crew'])

class IsCustomer(IsUserInGroup):
    """
    Permiso personalizado para permitir acceso solo a los miembros del grupo 'Customers'.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view, groups=['Customers'])

class IsManager(IsUserInGroup):
    """
    Permiso personalizado para permitir acceso solo a los managers.
    """
    def has_permission(self, request, view):
        return super().has_permission(request, view, groups=['Manager'])

class IsAdmin(BasePermission):
    """
    Permiso personalizado para permitir acceso solo a los superusuarios (admins).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser