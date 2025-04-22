from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Category, Order, Cart
from .serializers import CreateOrderSerializer, MenuItemSerializer, CartSerializer, CategorySerializer, AssignDeliveryCrewSerializer, OrderSerializer
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.decorators import action
from rest_framework.views import APIView

class IsManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow managers or admins to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_superuser or 
            request.user.groups.filter(name='Manager').exists()
        )

class IsDeliveryCrew(permissions.BasePermission):
    """
    Custom permission to only allow delivery crew members to access the view.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.groups.filter(name='Delivery crew').exists()
        )

class MenuItemViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows menu items to be viewed or edited.
    """
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
   
    def get_permissions(self):
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

    def get_permissions(self):
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

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            self.permission_classes = [permissions.AllowAny]
        return super().get_permissions()
     
class OrderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows orders to be viewed or edited.
    - Managers/Admins can see all orders
    - Delivery crew can see orders assigned to them
    - Customers can see their own orders
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        
        else:  # Regular customers
            return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        elif self.request.method in ['PATCH', 'PUT']:
            if self.request.user.groups.filter(name='Delivery crew').exists():
                data = self.request.data
                if set(data.keys()) - {'status'}:
                    raise PermissionDenied("Delivery crew can only update order status")
            else:
                self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        return super().get_permissions()
    
class CartViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows cart items to be viewed or edited.
    Only allows authenticated users to view and modify their own cart.
    """
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        unit_price = menuitem.price
        serializer.save(
            user=self.request.user,
            unit_price=unit_price,
            price=unit_price * serializer.validated_data['quantity']
        )
        
    def perform_update(self, serializer):
        menuitem = serializer.validated_data.get('menuitem', serializer.instance.menuitem)
        quantity = serializer.validated_data.get('quantity', serializer.instance.quantity)
        unit_price = menuitem.price
        serializer.save(unit_price=unit_price, price=unit_price * quantity)

class CreateOrderView(generics.CreateAPIView):
    """
    Allows customers to create an order based on their cart items.
    """
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = self.request.user

        if not (user.groups.filter(name='Customers').exists() or user.is_superuser):
            raise PermissionDenied("You don't have permission to perform this action.")

        # Check if cart is empty
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError("Your cart is empty.")

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        order = serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

from rest_framework.decorators import action

class AssignDeliveryCrewViewSet(viewsets.ViewSet):
    """
    A ViewSet to manage the assignment of delivery crew to orders.
    """
    permission_classes = [IsManagerOrAdmin]

    @action(detail=True, methods=['put'])
    def assign_delivery_crew(self, request, pk=None):
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        delivery_crew_id = request.data.get('delivery_crew')

        if not delivery_crew_id:
            return Response({"detail": "Delivery crew must be specified."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_crew = User.objects.get(id=delivery_crew_id)
            if not delivery_crew.groups.filter(name='Delivery crew').exists():
                return Response({"detail": "User is not in the Delivery crew group."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"detail": "Delivery crew user not found."}, status=status.HTTP_404_NOT_FOUND)

        order.delivery_crew = delivery_crew
        order.save()

        return Response({
            "detail": "Delivery crew assigned successfully.",
            "order_id": order.id,
            "delivery_crew": delivery_crew.username
        }, status=status.HTTP_200_OK)