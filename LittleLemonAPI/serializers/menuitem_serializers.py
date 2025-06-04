from rest_framework import serializers
from ..models import MenuItem, Category
from .category_serializers import CategorySerializer


class MenuItemSerializer(serializers.ModelSerializer):
    # Se escribe la categoría por su PK (ID)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    # Se expone el detalle completo de la categoría para lectura
    category_detail = CategorySerializer(source='category', read_only=True)

    class Meta:
        model = MenuItem
        fields = [
            'id',
            'title',
            'description',
            'price',
            'featured',
            'category',         # Para escritura (ID)
            'category_detail',  # Para lectura (objeto anidado)
        ]
        read_only_fields = ['id']