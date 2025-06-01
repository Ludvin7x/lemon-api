from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404
from ..models import  Order, Cart
from ..serializers import (
    OrderSerializer,
    CreateOrderSerializer
)
from ..permissions import IsAdmin, IsManagerOrAdmin, IsCustomer

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'delivery_crew', 'user']
    ordering_fields = ['date', 'status']

    def get_permissions(self):
        if self.action == 'destroy':
            self.permission_classes = [IsAuthenticated, (IsManagerOrAdmin | IsAdmin)]
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
        return [IsAuthenticated(), (IsManagerOrAdmin() | IsAdmin())]

    def put(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        crew_id = request.data.get('delivery_crew')
        crew = get_object_or_404(User, pk=crew_id)
        if not crew.groups.filter(name='Delivery crew').exists():
            raise ValidationError("User is not in the Delivery crew group.")
        order.delivery_crew = crew
        order.save()
        return Response({'detail': 'Delivery crew assigned successfully.'}, status=status.HTTP_200_OK)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.request.user.is_authenticated:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
