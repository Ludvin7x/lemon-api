from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from .models import Category, MenuItem
import os

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    # Grupos
    Group.objects.get_or_create(name="Manager")
    Group.objects.get_or_create(name="Delivery crew")
    Group.objects.get_or_create(name="Customer")

    # Usuarios de prueba
    if not User.objects.filter(username="customer").exists():
        user = User.objects.create_user("customer", password="test1234")
        customer_group = Group.objects.get(name="Customer")
        user.groups.add(customer_group)

    if not User.objects.filter(username="delivery").exists():
        user = User.objects.create_user("delivery", password="test1234")
        delivery_group = Group.objects.get(name="Delivery crew")
        user.groups.add(delivery_group)

 # Create superuser for Manager with hardcoded username/email and env var password
        mgr_username = "manager"
        mgr_email = "manager@lemon.com"
        mgr_password = os.environ.get("MANAGER_PASSWORD")
        if mgr_password and not User.objects.filter(username=mgr_username).exists():
            User.objects.create_superuser(
                username=mgr_username,
                email=mgr_email,
                password=mgr_password
            )


    # Categorías y MenuItems
    categories_data = [
        {"title": "Pizzas", "slug": "pizzas", "items": [
            {"title": "Margherita", "price": 10.99, "featured": True},
            {"title": "Pepperoni", "price": 12.50, "featured": False},
            {"title": "Vegetarian", "price": 11.25, "featured": False},
            {"title": "Hawaiian", "price": 13.00, "featured": False},
            {"title": "BBQ Chicken", "price": 14.25, "featured": True},
        ]},
        {"title": "Burgers", "slug": "burgers", "items": [
            {"title": "Classic Burger", "price": 8.99, "featured": True},
            {"title": "Cheeseburger", "price": 9.50, "featured": False},
            {"title": "Bacon Burger", "price": 10.75, "featured": False},
            {"title": "Veggie Burger", "price": 9.25, "featured": False},
            {"title": "Chicken Burger", "price": 9.99, "featured": True},
        ]},
        {"title": "Pasta", "slug": "pasta", "items": [
            {"title": "Spaghetti Carbonara", "price": 13.99, "featured": True},
            {"title": "Lasagna", "price": 14.50, "featured": False},
            {"title": "Penne Arrabbiata", "price": 12.25, "featured": False},
            {"title": "Mac & Cheese", "price": 11.99, "featured": False},
            {"title": "Fettuccine Alfredo", "price": 13.50, "featured": True},
        ]},
        {"title": "Salads", "slug": "salads", "items": [
            {"title": "Caesar Salad", "price": 7.99, "featured": True},
            {"title": "Greek Salad", "price": 8.25, "featured": False},
            {"title": "Caprese Salad", "price": 8.50, "featured": False},
            {"title": "Chicken Salad", "price": 9.00, "featured": False},
            {"title": "Tuna Salad", "price": 9.50, "featured": True},
        ]},
        {"title": "Drinks", "slug": "drinks", "items": [
            {"title": "Coke", "price": 1.99, "featured": True},
            {"title": "Sprite", "price": 1.99, "featured": False},
            {"title": "Lemonade", "price": 2.50, "featured": False},
            {"title": "Iced Tea", "price": 2.00, "featured": False},
            {"title": "Water", "price": 1.50, "featured": True},
        ]},
    ]

    # Crear categorías y items
    for category_data in categories_data:
        # Check if the category already exists to avoid duplicates
        category, created = Category.objects.get_or_create(
            title=category_data["title"], slug=category_data["slug"]
        )
        
        # If category is created, insert items
        if created:
            for item_data in category_data["items"]:
                MenuItem.objects.get_or_create(
                    title=item_data["title"],
                    price=item_data["price"],
                    featured=item_data["featured"],
                    category=category
                )