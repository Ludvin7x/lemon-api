from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from ..models import  Cart
from ..serializers import (
    CartSerializer
)

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

    @action(detail=False, methods=['delete'], url_path='clear')
    def clear(self, request):
        self.get_queryset().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)