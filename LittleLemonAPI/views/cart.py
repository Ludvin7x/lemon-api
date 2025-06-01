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

    @action(detail=False, methods=['delete'], url_path='', permission_classes=[IsAuthenticated])
    def clear(self, request):
        # DELETE /cart/menu-items/ clears all items
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)