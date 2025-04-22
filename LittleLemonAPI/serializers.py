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

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date', 'items']
        read_only_fields = ['user', 'items']

    def create(self, validated_data):
        order_items_data = validated_data.pop('items', [])
        order = Order.objects.create(**validated_data)
        for item_data in order_items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        order_items_data = validated_data.pop('items', [])
        instance.user = validated_data.get('user', instance.user)
        instance.delivery_crew = validated_data.get('delivery_crew', instance.delivery_crew)
        instance.status = validated_data.get('status', instance.status)
        instance.total = validated_data.get('total', instance.total)
        instance.date = validated_data.get('date', instance.date)
        instance.save()

        # Update or create order items
        for item_data in order_items_data:
            item_id = item_data.get('id')
            if item_id:
                try:
                    item_instance = OrderItem.objects.get(id=item_id, order=instance)
                    item_instance.menuitem = item_data.get('menuitem', item_instance.menuitem)
                    item_instance.quantity = item_data.get('quantity', item_instance.quantity)
                    item_instance.unit_price = item_data.get('unit_price', item_instance.unit_price)
                    item_instance.price = item_data.get('price', item_instance.price)
                    item_instance.save()
                except OrderItem.DoesNotExist:
                    OrderItem.objects.create(order=instance, **item_data)
            else:
                OrderItem.objects.create(order=instance, **item_data)

        return instance
 
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
        validated_data['user'] = user

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            menuitem=validated_data['menuitem'],
            defaults={
                'quantity': validated_data['quantity'],
                'unit_price': validated_data['unit_price'],
                'price': validated_data['quantity'] * validated_data['unit_price']
            }
        )

        if not created:
            cart_item.quantity += validated_data['quantity']
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

        order = Order.objects.create(
            user=user, 
            date=timezone.now().date(),
            total=sum(item.price for item in cart_items)
        )

        order_items = []
        for item in cart_items:
            order_items.append(OrderItem(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            ))

        OrderItem.objects.bulk_create(order_items)
        cart_items.delete()

        return order