from rest_framework import serializers
from ..models import Cart
from .menuitem_serializers import MenuItemSerializer

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    user = serializers.StringRelatedField()
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

    def create(self, validated_data):
        menuitem = validated_data['menuitem']
        qty = validated_data['quantity']
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = menuitem.price * qty
        return super().create(validated_data)

    def update(self, instance, validated_data):
        menuitem = validated_data.get('menuitem', instance.menuitem)
        qty = validated_data.get('quantity', instance.quantity)
        instance.unit_price = menuitem.price
        instance.price = menuitem.price * qty
        instance.save()
        return instance
