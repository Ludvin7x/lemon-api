from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category']

class CartSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    user = serializers.StringRelatedField()
    class Meta:
        model = Cart
        fields = ['id', 'user', 'menuitem', 'quantity', 'unit_price', 'price']
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
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

class OrderItemSerializer(serializers.ModelSerializer):
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = OrderItem
        fields = ['id', 'menuitem', 'quantity', 'unit_price', 'price']
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    def save(self, *args, **kwargs):
        self.unit_price = self.menuitem.price
        self.price = self.unit_price * self.quantity
        return super().save(*args, **kwargs)

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()
    delivery_crew = serializers.StringRelatedField()
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'items']
    def validate_status(self, value):
        allowed = ['pending','preparing','delivering','delivered','cancelled']
        if value not in allowed:
            raise serializers.ValidationError(f"Invalid status. Must be one of {allowed}.")
        return value

class CreateOrderSerializer(serializers.ModelSerializer):
    # we don’t actually accept “items” here — we build from the Cart on the server
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','total','date']
        read_only_fields = ['id','total','date','user']
    def create(self, validated_data):
        user = self.context['request'].user
        # pull all Cart items for this user
        cart_qs = Cart.objects.filter(user=user)
        if not cart_qs.exists():
            raise serializers.ValidationError("Your cart is empty.")
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
        # clear cart
        cart_qs.delete()
        return order