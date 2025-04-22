from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, OrderItem
from django.utils import timezone
from django.contrib.auth.models import User, Group

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class AssignDeliveryCrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['delivery_crew']

    def validate_delivery_crew(self, value):
        if value and not value.groups.filter(name='Delivery crew').exists():
            raise serializers.ValidationError("The user is not a delivery crew member.")
        return value

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['unit_price', 'price']  # Evitamos que el cliente los modifique

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True, source='orderitem_set')  # Mejor nombre + source explícito

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'order_items']
        read_only_fields = ['user', 'order_items']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
        read_only_fields = ['user', 'unit_price', 'price']

    def validate(self, data):
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        menuitem = validated_data['menuitem']
        quantity = validated_data['quantity']

        validated_data['user'] = user
        validated_data['unit_price'] = menuitem.price
        validated_data['price'] = quantity * menuitem.price

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            menuitem=menuitem,
            defaults={
                'quantity': quantity,
                'unit_price': validated_data['unit_price'],
                'price': validated_data['price']
            }
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.price = cart_item.quantity * cart_item.unit_price
            cart_item.save()

        return cart_item

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total', 'date']
        read_only_fields = ['id', 'total', 'date']

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = Cart.objects.filter(user=user)

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        total = sum(item.price for item in cart_items)

        order = Order.objects.create(
            user=user, 
            date=timezone.now().date(),
            total=total
        )

        order_items = [
            OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            ) for item in cart_items
        ]

        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()

        return order