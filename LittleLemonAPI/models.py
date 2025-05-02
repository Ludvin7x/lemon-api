from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255, db_index=True, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="menu_items")

    def __str__(self):
        return f"{self.title} - ${self.price}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_items")
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def save(self, *args, **kwargs):
        self.unit_price = self.menuitem.price
        self.price = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('menuitem', 'user')
        verbose_name_plural = "Cart Items"

    def __str__(self):
        return f"{self.user.username}'s cart - {self.menuitem.title} x{self.quantity}"


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PREPARING = 'preparing'
    STATUS_DELIVERING = 'delivering'
    STATUS_DELIVERED = 'delivered'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_DELIVERING, 'Out for delivery'),
        (STATUS_DELIVERED, 'Delivered'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    delivery_crew = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deliveries",
        limit_choices_to={'groups__name': 'Delivery crew'}
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True
    )
    total = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Order #{self.id} - {self.user.username} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menuitem = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        unique_together = ('order', 'menuitem')
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.menuitem.title} x{self.quantity} for Order #{self.order.id}"

    def save(self, *args, **kwargs):
        self.unit_price = self.menuitem.price
        self.price = self.unit_price * self.quantity
        super().save(*args, **kwargs)