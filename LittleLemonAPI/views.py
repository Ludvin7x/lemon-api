from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User, Group
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import MenuItem, Category, Order, Cart
from .serializers import (
    MenuItemSerializer, CategorySerializer, CartSerializer,
    OrderSerializer, CreateOrderSerializer
)
from .permissions import IsAdmin, IsManager, IsCustomer


class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['category']
    ordering_fields = ['title', 'price']
    search_fields = ['title']

def get_permissions(self):
    if self.action in ['list', 'retrieve']:
        permission_classes = [AllowAny]
    elif self.action in ['create', 'update', 'partial_update', 'destroy']:
        permission_classes = [IsAuthenticated, IsManager | IsAdmin]
    else:
        permission_classes = [IsAuthenticated]
    return [permission() for permission in permission_classes]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, (IsManager | IsAdmin)]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    filter_backends = []

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=False, methods=['delete'], url_path='', permission_classes=[IsAuthenticated])
    def clear(self, request):
        # DELETE /cart/menu-items/ clears all items
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'delivery_crew', 'user']
    ordering_fields = ['date', 'status']

    def get_permissions(self):
        if self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, (IsManager | IsAdmin)]
        elif self.action in ['update', 'partial_update'] and self.request.user.groups.filter(name='Delivery crew').exists():
            data_keys = set(self.request.data.keys())
            if data_keys - {'status'}:
                raise PermissionDenied("Delivery crew can only update order status")
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name='Manager').exists():
            return Order.objects.all()
        if user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)
        return Order.objects.filter(user=user)


class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer

    def get_permissions(self):
        return [IsAuthenticated(), (IsCustomer() | IsAdmin())]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user = request.user
        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            raise ValidationError("Your cart is empty.")
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        cart_items.delete()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class AssignDeliveryCrewView(APIView):
    def get_permissions(self):
        return [IsAuthenticated(), (IsManager() | IsAdmin())]

    def put(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        crew_id = request.data.get('delivery_crew')
        crew = get_object_or_404(User, pk=crew_id)
        if not crew.groups.filter(name='Delivery crew').exists():
            raise ValidationError("User is not in the Delivery crew group.")
        order.delivery_crew = crew
        order.save()
        return Response({'detail': 'Delivery crew assigned successfully.'}, status=status.HTTP_200_OK)


class ManagerGroupView(APIView):
    group_name = 'Manager'

    def get_permissions(self):
        return [IsAuthenticated(), (IsManager() | IsAdmin())]

    def get(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        users = [{'id': u.id, 'username': u.username} for u in group.user_set.all()]
        return Response(users)

    def post(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        user = get_object_or_404(User, pk=request.data.get('user_id'))
        group.user_set.add(user)
        return Response({'detail': 'User added to Manager group.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        group = get_object_or_404(Group, name=self.group_name)
        user = get_object_or_404(User, pk=user_id)
        group.user_set.remove(user)
        return Response({'detail': 'User removed from Manager group.'}, status=status.HTTP_200_OK)


class DeliveryCrewGroupView(APIView):
    group_name = 'Delivery crew'

    def get_permissions(self):
        return [IsAuthenticated(), (IsManager() | IsAdmin())]

    def get(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        users = [{'id': u.id, 'username': u.username} for u in group.user_set.all()]
        return Response(users)

    def post(self, request):
        group = get_object_or_404(Group, name=self.group_name)
        user = get_object_or_404(User, pk=request.data.get('user_id'))
        group.user_set.add(user)
        return Response({'detail': 'User added to Delivery crew group.'}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        group = get_object_or_404(Group, name=self.group_name)
        user = get_object_or_404(User, pk=user_id)
        group.user_set.remove(user)
        return Response({'detail': 'User removed from Delivery crew group.'}, status=status.HTTP_200_OK)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "OK"})

class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.user.is_authenticated:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.user.is_authenticated:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.user.is_authenticated:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()