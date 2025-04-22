from django.shortcuts import render
from rest_framework import viewsets, permissions, generics
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Category, Order, Cart
from .serializers import MenuItemSerializer,CartSerializer, CategorySerializer, AssignDeliveryCrewSerializer, OrderSerializer
from .permissions import IsManagerOrAdmin

class IsManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow managers to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.groups.filter(name='Manager').exists()
        )
class MenuItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows menu items to be viewed or edited.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
   
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()
    
class CategoryListView(generics.ListCreateAPIView):
    """
    API endpoint that allows categories to be viewed or created.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows a category to be viewed, updated or deleted.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()
    
class AssignDeliveryCrewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows managers to assign delivery crew to orders.
    """
    queryset = Order.objects.all()
    serializer_class = AssignDeliveryCrewSerializer
    permission_classes = [IsAuthenticated, IsManagerOrAdmin]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()
    
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be viewed or edited.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()
    
class CartViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cart items to be viewed or edited.
    """
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()