from rest_framework import serializers
from ..models import Cart
from ..models import MenuItem
from .menuitem_serializers import MenuItemSerializer

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)                      # Info expandida para mostrar
    menuitem_id = serializers.PrimaryKeyRelatedField(                 # Solo para escritura
        queryset=MenuItem.objects.all(), write_only=True
    )
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'menuitem',     # → Read only
            'menuitem_id',  # → Write only
            'quantity',
            'unit_price',
            'price'
        ]
        read_only_fields = ['unit_price', 'price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data.pop('menuitem_id')
        quantity = validated_data['quantity']
        unit_price = menuitem.price
        price = unit_price * quantity

        # Verifica si ya existe el ítem para el usuario → actualiza cantidad
        cart_item, created = Cart.objects.get_or_create(
            user=user,
            menuitem=menuitem,
            defaults={
                'quantity': quantity,
                'unit_price': unit_price,
                'price': price,
            }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.unit_price = unit_price
            cart_item.price = cart_item.quantity * unit_price
            cart_item.save()

        return cart_item

    def update(self, instance, validated_data):
        quantity = validated_data.get('quantity', instance.quantity)
        instance.quantity = quantity
        instance.price = instance.unit_price * quantity
        instance.save()
        return instance