from rest_framework import serializers
from ..models import Order, OrderItem, Cart
from .menuitem_serializers import MenuItemSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than zero.')
        return value

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    delivery_crew = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'items']

    def validate_status(self, value):
        allowed = ['pending', 'preparing', 'delivering', 'delivered', 'cancelled']
        if value not in allowed:
            raise serializers.ValidationError(f'Invalid status. Must be one of {allowed}.')
        return value

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']
        read_only_fields = ['id', 'total', 'date', 'user']

    def create(self, validated_data):
        user = self.context['request'].user
        cart_qs = Cart.objects.filter(user=user)
        if not cart_qs.exists():
            raise serializers.ValidationError('Your cart is empty.')
        total = 0
        order = Order.objects.create(user=user, **validated_data)
        for cart_item in cart_qs:
            OrderItem.objects.create(
                order=order,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
            total += cart_item.price
        order.total = total
        order.save()
        cart_qs.delete()
        return order
