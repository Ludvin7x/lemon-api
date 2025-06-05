from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.db import connection
from .models import Category, MenuItem
import os

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    # Avoid execution if tables don't exist yet
    try:
        # Check if the 'LittleLemonAPI_menuitem' table exists as a proxy for app tables being ready
        if "LittleLemonAPI_menuitem" not in connection.introspection.table_names():
            return
    except Exception as e:
        print(f"Signal cancelled: {e}")
        return

    # Create or get groups
    for group_name in ["Manager", "Delivery crew", "Customer"]:
        Group.objects.get_or_create(name=group_name)

    # Create or update test users
    users_data = [
        {"username": "customer", "email": "customer@example.com", "password": "test1234", "group": "Customer"},
        {"username": "delivery", "email": "delivery@example.com", "password": "test1234", "group": "Delivery crew"},
    ]

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data["username"],
            defaults={"email": user_data["email"], "password": user_data["password"]}
        )
        if not created:
            # If user already exists, update email and set password (Django handles hashing)
            user.email = user_data["email"]
            user.set_password(user_data["password"])
            user.save()
        
        # Add user to the specified group
        group = Group.objects.get(name=user_data["group"])
        user.groups.add(group)

    # Create superuser from environment variable
    mgr_username = "manager"
    mgr_email = "manager@lemon.com"
    mgr_password = os.environ.get("MANAGER_PASSWORD")
    if mgr_password:
        # Use get_or_create for manager, and if it exists, ensure it's a superuser and email is correct.
        # Note: update_or_create is more direct for this, but get_or_create with subsequent updates also works.
        manager_user, created = User.objects.get_or_create(
            username=mgr_username,
            defaults={
                "email": mgr_email,
                "password": mgr_password,
                "is_staff": True,
                "is_superuser": True,
            }
        )
        if not created:
            # If manager exists, update email and ensure superuser status
            manager_user.email = mgr_email
            manager_user.is_staff = True
            manager_user.is_superuser = True
            manager_user.set_password(mgr_password) # Make sure password is set/updated
            manager_user.save()


    # Initial data: Categories + Items
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