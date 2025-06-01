from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated
from ..serializers import CategorySerializer
from ..models import Category
from ..permissions import IsManagerOrAdmin

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CategoryListView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['POST']:
            permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:  # GET list
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            permission_classes = [IsAuthenticated, IsManagerOrAdmin]
        else:  # GET detail
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]