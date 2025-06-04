from rest_framework import viewsets, generics, permissions
from rest_framework.permissions import IsAuthenticated
from ..serializers import CategorySerializer
from ..models import Category
from ..permissions import IsManagerOrAdmin

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para /api/categories/
    GET    -> público
    POST   -> autenticado y manager/admin
    PUT    -> autenticado y manager/admin
    DELETE -> autenticado y manager/admin
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsManagerOrAdmin()]
        return [permissions.AllowAny()]  # público para list y retrieve


class CategoryListView(generics.ListCreateAPIView):
    """
    GET  /api/categories/   -> público
    POST /api/categories/   -> Manager o Admin
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsManagerOrAdmin()]


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/categories/<id>/ -> autenticado
    PUT    /api/categories/<id>/ -> manager/admin
    DELETE /api/categories/<id>/ -> manager/admin
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated(), IsManagerOrAdmin()]
        return [permissions.IsAuthenticated()]