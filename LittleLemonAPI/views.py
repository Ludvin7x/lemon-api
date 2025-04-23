from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAuthenticated
from .models import MenuItem, Category, Order, Cart
from .serializers import (
    CreateOrderSerializer, MenuItemSerializer, CartSerializer,
    CategorySerializer, AssignDeliveryCrewSerializer, OrderSerializer
)
from django.contrib.auth.models import User, Group
from django.db import transaction
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from .permissions import IsAdmin, IsManager, IsDeliveryCrew, IsCustomer
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import MenuItem
from .serializers import MenuItemSerializer
from .permissions import IsManager, IsAdmin
from rest_framework.permissions import IsAuthenticated

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['category']
    ordering_fields = ['title', 'price']  
    ordering = ['title']  
    search_fields = ['title'] 

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManager | IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated, IsManager | IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            self.permission_classes = [IsAuthenticated, IsManager | IsAdmin]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['status', 'delivery_crew', 'user']  # Filtrar por estado, delivery_crew o usuario
    ordering_fields = ['created_at', 'status']  # Ordenar por fecha de creación o estado
    ordering = ['created_at']  # Orden predeterminado por fecha de creación

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        else:
            return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.request.method == 'DELETE':
            self.permission_classes = [IsAuthenticated, IsManager | IsAdmin]
        elif self.request.method in ['PATCH', 'PUT']:
            if self.request.user.groups.filter(name='Delivery crew').exists():
                data = self.request.data
                if set(data.keys()) - {'status'}:
                    raise PermissionDenied("Delivery crew can only update order status")
            else:
                self.permission_classes = [IsAuthenticated, IsManager | IsAdmin]
        return super().get_permissions()


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

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
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated, IsCustomer | IsAdmin]

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = self.request.user

        if not (user.groups.filter(name='Customers').exists() or user.is_superuser):
            raise PermissionDenied("You don't have permission to perform this action.")

        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError("Your cart is empty.")

        # Crear el pedido
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        order = serializer.save()

        # Eliminar ítems del carrito después de crear el pedido
        cart_items.delete()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class AssignDeliveryCrewView(APIView):
    permission_classes = [IsAuthenticated, IsManager | IsAdmin]

    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        delivery_crew_id = request.data.get('delivery_crew')
        if not delivery_crew_id:
            return Response({"detail": "Delivery crew must be specified."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            delivery_crew = User.objects.get(pk=delivery_crew_id)
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


class GroupUserManagementView(APIView):
    permission_classes = [IsAuthenticated, IsManager | IsAdmin]
    group_name = None  # Se define en las subclases

    def get_group(self):
        return Group.objects.get(name=self.group_name)

    def get(self, request):
        group = self.get_group()
        users = group.user_set.all()
        data = [{'id': user.id, 'username': user.username} for user in users]
        return Response(data)

    def post(self, request):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        group = self.get_group()
        group.user_set.add(user)
        return Response({"message": f"User {user.username} added to {self.group_name} group."}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        group = self.get_group()
        user = User.objects.filter(id=user_id).first()
        if not user:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        if user not in group.user_set.all():
            return Response({"error": "User not in group."}, status=status.HTTP_404_NOT_FOUND)

        group.user_set.remove(user)
        return Response({"message": f"User {user.username} removed from {self.group_name} group."}, status=status.HTTP_200_OK)


class ManagerGroupView(GroupUserManagementView):
    group_name = 'Manager'


class DeliveryCrewGroupView(GroupUserManagementView):
    group_name = 'Delivery crew'

class HealthCheckView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({"status": "OK"}, status=status.HTTP_200_OK)