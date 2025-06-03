from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.db import connection
from .models import Category, MenuItem
import os

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    # Evitar ejecución si las tablas no existen todavía
    try:
        if "LittleLemonAPI_menuitem" not in connection.introspection.table_names():
            return
    except Exception as e:
        print(f"Signal cancelado: {e}")
        return

    # Crear grupos
    for group_name in ["Manager", "Delivery crew", "Customer"]:
        Group.objects.get_or_create(name=group_name)

    # Crear usuarios de prueba
    if not User.objects.filter(username="customer").exists():
        user = User.objects.create_user("customer", password="test1234")
        user.groups.add(Group.objects.get(name="Customer"))

    if not User.objects.filter(username="delivery").exists():
        user = User.objects.create_user("delivery", password="test1234")
        user.groups.add(Group.objects.get(name="Delivery crew"))

    # Crear superusuario desde variable de entorno
    mgr_username = "manager"
    mgr_email = "manager@lemon.com"
    mgr_password = os.environ.get("MANAGER_PASSWORD")
    if mgr_password and not User.objects.filter(username=mgr_username).exists():
        User.objects.create_superuser(username=mgr_username, email=mgr_email, password=mgr_password)

    # Datos iniciales: Categorías + Items
    categories_data = [
        {"title": "Pizzas", "slug": "pizzas", "items": [
            {"title": "Margherita", "description": "Tomato, mozzarella, and basil.", "price": 10.99, "featured": True},
            {"title": "Pepperoni", "description": "Pepperoni and cheese.", "price": 12.50, "featured": False},
            {"title": "BBQ Chicken", "description": "BBQ sauce and chicken.", "price": 13.50, "featured": True},
            {"title": "Hawaiian", "description": "Ham and pineapple.", "price": 11.75, "featured": False},
        ]},
        {"title": "Pasta", "slug": "pasta", "items": [
            {"title": "Spaghetti Bolognese", "description": "Traditional meat sauce.", "price": 11.99, "featured": True},
            {"title": "Fettuccine Alfredo", "description": "Creamy parmesan sauce.", "price": 12.25, "featured": False},
        ]},
        {"title": "Salads", "slug": "salads", "items": [
            {"title": "Caesar Salad", "description": "Romaine, croutons, and parmesan.", "price": 9.50, "featured": False},
            {"title": "Greek Salad", "description": "Feta, olives, cucumbers, tomatoes.", "price": 8.75, "featured": True},
        ]},
        {"title": "Burgers", "slug": "burgers", "items": [
            {"title": "Classic Cheeseburger", "description": "Beef patty, cheese, lettuce, tomato.", "price": 10.25, "featured": True},
            {"title": "Bacon Burger", "description": "With crispy bacon.", "price": 11.50, "featured": False},
        ]},
        {"title": "Desserts", "slug": "desserts", "items": [
            {"title": "Chocolate Cake", "description": "Dark chocolate layered cake.", "price": 5.99, "featured": True},
            {"title": "Cheesecake", "description": "Creamy NY-style cheesecake.", "price": 6.25, "featured": False},
            {"title": "Tiramisu", "description": "Espresso and mascarpone layers.", "price": 5.75, "featured": False},
        ]},
        {"title": "Drinks", "slug": "drinks", "items": [
            {"title": "Lemonade", "description": "Freshly squeezed lemon juice.", "price": 3.50, "featured": True},
            {"title": "Iced Tea", "description": "Cold black tea with lemon.", "price": 3.25, "featured": False},
            {"title": "Espresso", "description": "Strong shot of espresso.", "price": 2.50, "featured": False},
        ]},
        {"title": "Seafood", "slug": "seafood", "items": [
            {"title": "Grilled Salmon", "description": "Served with lemon butter.", "price": 16.99, "featured": True},
            {"title": "Shrimp Pasta", "description": "Pasta with shrimp and garlic sauce.", "price": 15.50, "featured": False},
        ]},
    ]

    for category_data in categories_data:
        category, _ = Category.objects.get_or_create(title=category_data["title"], slug=category_data["slug"])
        for item in category_data["items"]:
            MenuItem.objects.get_or_create(
                title=item["title"],
                category=category,
                defaults={
                    "description": item["description"],
                    "price": item["price"],
                    "featured": item["featured"],
                }
            )