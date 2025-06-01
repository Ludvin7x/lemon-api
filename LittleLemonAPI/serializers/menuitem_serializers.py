from rest_framework import serializers
from ..models import MenuItem
from .category_serializers import CategorySerializer

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']
