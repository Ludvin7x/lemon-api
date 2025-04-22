from django.shortcuts import render
from rest_framework import viewsets, permissions, generics, status
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Category, Order, Cart
from .serializers import CreateOrderSerializer, MenuItemSerializer, CartSerializer, CategorySerializer, AssignDeliveryCrewSerializer, OrderSerializer
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError

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
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        validated_data = request.data
        instance.delivery_crew = validated_data.get('delivery_crew', instance.delivery_crew)
        instance.save()
        return Response(self.get_serializer(instance).data)
    
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
        """
        Customize permissions based on the action:
        - DELETE: Only managers/admins
        - PATCH/PUT: Managers/admins or delivery crew (limited fields)
        - GET: Any authenticated user (but queryset will be filtered)
        """
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        elif self.request.method in ['PATCH', 'PUT']:
            if self.request.user.groups.filter(name='Delivery crew').exists():
                # Delivery crew can only update status
                data = self.request.data
                if set(data.keys()) - {'status'}:
                    raise PermissionDenied("Delivery crew can only update order status")
            else:
                # Managers can update anything
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
        # Get menuitem from the validated data
        menuitem = serializer.validated_data['menuitem']
        # Get the price directly from the MenuItem in the database
        unit_price = menuitem.price
        # Save the cart item with the correct price from the database
        serializer.save(
            user=self.request.user,
            unit_price=unit_price,
            price=unit_price * serializer.validated_data['quantity']
        )
        
    def perform_update(self, serializer):
        # For updates, make sure the price is recalculated
        menuitem = serializer.validated_data.get('menuitem', serializer.instance.menuitem)
        quantity = serializer.validated_data.get('quantity', serializer.instance.quantity)
        # Always use the price from the database, not from the request
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

        # Check if user is in the Customers group
        if not (user.groups.filter(name='Customers').exists() or user.is_superuser):
            raise PermissionDenied("You don't have permission to perform this action.")

        # Create serializer and validate
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Save the order
        order = serializer.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    