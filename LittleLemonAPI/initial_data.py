import logging
from django.contrib.auth.models import User, Group
from django.db import transaction
from .models import Category, MenuItem

def run():
    # Configuración del logger
    logger = logging.getLogger(__name__)

    try:
        # Crear grupos si no existen
        for group_name in ['Manager', 'Delivery crew', 'Customers']:
            Group.objects.get_or_create(name=group_name)

        # Crear usuarios con roles
        # Delivery Crew
        delivery, _ = User.objects.get_or_create(username='delivery')
        delivery.set_password('delivery123')
        delivery.save()
        delivery_group, _ = Group.objects.get_or_create(name='Delivery crew')
        delivery_group.user_set.add(delivery)

        # Customer
        customer, _ = User.objects.get_or_create(username='customer')
        customer.set_password('customer123')
        customer.save()
        customers_group, _ = Group.objects.get_or_create(name='Customers')
        customers_group.user_set.add(customer)

        logger.info("Users and groups created successfully.")

        # Crear categorías e ítems si no existen
        if not Category.objects.exists():
            logger.info("Seeding initial categories and menu items...")

            categories = [
                {"slug": "appetizers", "title": "Appetizers"},
                {"slug": "main-dishes", "title": "Main Dishes"},
                {"slug": "desserts", "title": "Desserts"},
                {"slug": "beverages", "title": "Beverages"},
                {"slug": "vegan", "title": "Vegan"},
            ]

            items_by_category = {
                "Appetizers": [
                    ("Bruschetta", 6.50),
                    ("Garlic Bread", 5.00),
                    ("Stuffed Mushrooms", 7.25),
                    ("Fried Calamari", 8.90),
                    ("Caprese Skewers", 6.75),
                ],
                "Main Dishes": [
                    ("Grilled Salmon", 18.50),
                    ("Chicken Alfredo", 16.00),
                    ("Beef Lasagna", 15.75),
                    ("Margherita Pizza", 13.00),
                    ("Spaghetti Bolognese", 14.25),
                ],
                "Desserts": [
                    ("Tiramisu", 6.50),
                    ("Chocolate Lava Cake", 7.00),
                    ("Panna Cotta", 5.50),
                    ("Lemon Tart", 6.00),
                    ("Gelato Trio", 5.75),
                ],
                "Beverages": [
                    ("Espresso", 3.00),
                    ("Lemonade", 2.50),
                    ("Iced Tea", 2.75),
                    ("Cappuccino", 3.50),
                    ("Sparkling Water", 2.25),
                ],
                "Vegan": [
                    ("Vegan Buddha Bowl", 12.50),
                    ("Grilled Tofu Salad", 11.00),
                    ("Vegan Pasta Primavera", 13.25),
                    ("Lentil Soup", 9.00),
                    ("Stuffed Bell Peppers", 10.75),
                ],
            }

            # Usando transacciones para asegurar integridad de los datos
            with transaction.atomic():
                for cat in categories:
                    category = Category.objects.create(**cat)
                    for title, price in items_by_category[category.title]:
                        MenuItem.objects.create(
                            title=title,
                            price=price,
                            featured=False,
                            category=category
                        )

            logger.info("Initial data seeded successfully.")

    except Exception as e:
        # Log the exception if any occurs
        logger.error(f"Error during seeding: {e}")