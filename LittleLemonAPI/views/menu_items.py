from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from ..models import MenuItem
from ..serializers import MenuItemSerializer
from ..permissions import IsAdmin, IsManagerOrAdmin
from ..filters import MenuItemFilter
from ..throttles import MenuUserThrottle, MenuAnonThrottle

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all().order_by('id')
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_class = MenuItemFilter  
    ordering_fields = ['title', 'price']
    search_fields = ['title', 'description']  

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsManagerOrAdmin | IsAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_throttles(self):
        if self.action in ['list', 'retrieve']:
            return [MenuUserThrottle()] if self.request.user.is_authenticated else [MenuAnonThrottle()]
        return super().get_throttles()
