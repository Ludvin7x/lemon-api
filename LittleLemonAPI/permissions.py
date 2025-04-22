from rest_framework.permissions import BasePermission

class IsManagerOrAdmin(BasePermission):
    """
    Custom permission to allow access to Managers or Admins (superusers).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or request.user.groups.filter(name='Manager').exists()
        )