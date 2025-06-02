from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from .models import Category, MenuItem
import os

@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    # Group creation
    Group.objects.get_or_create(name="Manager")
    Group.objects.get_or_create(name="Delivery crew")
    Group.objects.get_or_create(name="Customer")

    # test users creation
    if not User.objects.filter(username="customer").exists():
        user = User.objects.create_user("customer", password="test1234")
        customer_group = Group.objects.get(name="Customer")
        user.groups.add(customer_group)

    if not User.objects.filter(username="delivery").exists():
        user = User.objects.create_user("delivery", password="test1234")
        delivery_group = Group.objects.get(name="Delivery crew")
        user.groups.add(delivery_group)

 # Create adminuser
        mgr_username = "manager"
        mgr_email = "manager@lemon.com"
        mgr_password = os.environ.get("MANAGER_PASSWORD")
        if mgr_password and not User.objects.filter(username=mgr_username).exists():
            User.objects.create_superuser(
                username=mgr_username,
                email=mgr_email,
                password=mgr_password
            )

    categories_data = [
        # 1
        {"title": "Pizzas", "slug": "pizzas", "items": [
            {"title": "Margherita",         "description": "Classic pizza with tomato, fresh mozzarella and basil.",
            "price": 10.99, "featured": True},
            {"title": "Pepperoni",          "description": "Loaded with pepperoni and mozzarella cheese.",
            "price": 12.50, "featured": False},
            {"title": "Vegetarian",         "description": "Topped with seasonal vegetables and light cheese.",
            "price": 11.25, "featured": False},
            {"title": "Hawaiian",           "description": "Ham, pineapple and mozzarella on tomato sauce.",
            "price": 13.00, "featured": False},
            {"title": "BBQ Chicken",        "description": "Grilled chicken, BBQ sauce and red onions.",
            "price": 14.25, "featured": True},
        ]},
        # 2
        {"title": "Burgers", "slug": "burgers", "items": [
            {"title": "Classic Burger",     "description": "Beef patty, lettuce, tomato and house sauce.",
            "price": 8.99,  "featured": True},
            {"title": "Cheeseburger",       "description": "Classic burger topped with cheddar cheese.",
            "price": 9.50,  "featured": False},
            {"title": "Bacon Burger",       "description": "Juicy burger with crispy bacon and pickles.",
            "price": 10.75, "featured": False},
            {"title": "Veggie Burger",      "description": "Grilled vegetable patty with avocado spread.",
            "price": 9.25,  "featured": False},
            {"title": "Chicken Burger",     "description": "Grilled chicken breast, lettuce and mayo.",
            "price": 9.99,  "featured": True},
        ]},
        # 3
        {"title": "Pasta", "slug": "pasta", "items": [
            {"title": "Spaghetti Carbonara","description": "Creamy sauce with pancetta and parmesan.",
            "price": 13.99, "featured": True},
            {"title": "Lasagna",            "description": "Layered pasta, beef ragù and béchamel.",
            "price": 14.50, "featured": False},
            {"title": "Penne Arrabbiata",   "description": "Spicy tomato sauce with garlic and chili.",
            "price": 12.25, "featured": False},
            {"title": "Mac & Cheese",       "description": "Elbow pasta baked in a cheddar cheese sauce.",
            "price": 11.99, "featured": False},
            {"title": "Fettuccine Alfredo", "description": "Rich cream sauce with parmesan and parsley.",
            "price": 13.50, "featured": True},
        ]},
        # 4
        {"title": "Salads", "slug": "salads", "items": [
            {"title": "Caesar Salad",       "description": "Romaine, parmesan, croutons and Caesar dressing.",
            "price": 7.99, "featured": True},
            {"title": "Greek Salad",        "description": "Tomato, cucumber, olives and feta cheese.",
            "price": 8.25, "featured": False},
            {"title": "Caprese Salad",      "description": "Fresh mozzarella, tomato and basil drizzle.",
            "price": 8.50, "featured": False},
            {"title": "Chicken Salad",      "description": "Grilled chicken over mixed greens and veggies.",
            "price": 9.00, "featured": False},
            {"title": "Tuna Salad",         "description": "Albacore tuna, sweet corn and red onions.",
            "price": 9.50, "featured": True},
        ]},
        # 5
        {"title": "Drinks", "slug": "drinks", "items": [
            {"title": "Coke",               "description": "Chilled classic Coca-Cola can (330 ml).",
            "price": 1.99, "featured": True},
            {"title": "Sprite",             "description": "Refreshing lemon-lime soda (330 ml).",
            "price": 1.99, "featured": False},
            {"title": "Lemonade",           "description": "House-made lemonade with fresh lemons.",
            "price": 2.50, "featured": False},
            {"title": "Iced Tea",           "description": "Brewed black tea served over ice.",
            "price": 2.00, "featured": False},
            {"title": "Water",              "description": "Still mineral water (500 ml).",
            "price": 1.50, "featured": True},
        ]},
        # 6
        {"title": "Desserts", "slug": "desserts", "items": [
            {"title": "Chocolate Cake",     "description": "Rich dark chocolate layered cake slice.",
            "price": 5.99, "featured": True},
            {"title": "Cheesecake",         "description": "Creamy New-York style cheesecake slice.",
            "price": 6.25, "featured": False},
            {"title": "Apple Pie",          "description": "Traditional apple pie with cinnamon.",
            "price": 4.99, "featured": False},
            {"title": "Tiramisu",           "description": "Italian mascarpone dessert with espresso.",
            "price": 5.75, "featured": False},
            {"title": "Ice Cream Sundae",   "description": "Vanilla ice cream with chocolate syrup.",
            "price": 4.50, "featured": True},
        ]},
        # 7
        {"title": "Soups", "slug": "soups", "items": [
            {"title": "Tomato Soup",        "description": "Smooth roasted-tomato soup with basil.",
            "price": 4.99, "featured": True},
            {"title": "Chicken Noodle",     "description": "Classic soup with chicken, pasta and veggies.",
            "price": 5.25, "featured": False},
            {"title": "Minestrone",         "description": "Hearty Italian vegetable soup.",
            "price": 5.50, "featured": False},
            {"title": "Broccoli Cheddar",   "description": "Creamy soup with broccoli and cheddar.",
            "price": 5.75, "featured": False},
            {"title": "French Onion",       "description": "Caramelized onion soup with melted gruyère.",
            "price": 6.00, "featured": True},
        ]},
        # 8
        {"title": "Sandwiches", "slug": "sandwiches", "items": [
            {"title": "Club Sandwich",      "description": "Triple-layer sandwich with turkey and bacon.",
            "price": 7.99, "featured": True},
            {"title": "BLT",                "description": "Bacon, lettuce and tomato on toasted bread.",
            "price": 6.75, "featured": False},
            {"title": "Grilled Cheese",     "description": "Melted cheddar on butter-toasted bread.",
            "price": 5.50, "featured": False},
            {"title": "Tuna Melt",          "description": "Tuna salad topped with melted Swiss cheese.",
            "price": 7.25, "featured": False},
            {"title": "Chicken Panini",     "description": "Grilled chicken with pesto and mozzarella.",
            "price": 8.25, "featured": True},
        ]},
        # 9
        {"title": "Breakfast", "slug": "breakfast", "items": [
            {"title": "Pancakes",           "description": "Fluffy stack served with maple syrup.",
            "price": 6.99, "featured": True},
            {"title": "French Toast",       "description": "Brioche slices dipped in egg custard.",
            "price": 7.25, "featured": False},
            {"title": "Omelette",           "description": "Three-egg omelette with choice of fillings.",
            "price": 7.50, "featured": False},
            {"title": "Breakfast Burrito",  "description": "Scrambled eggs, bacon and salsa in a tortilla.",
            "price": 8.25, "featured": False},
            {"title": "Avocado Toast",      "description": "Smashed avocado on multigrain bread.",
            "price": 7.99, "featured": True},
        ]},
        # 10
        {"title": "Seafood", "slug": "seafood", "items": [
            {"title": "Grilled Salmon",     "description": "Atlantic salmon fillet with lemon butter.",
            "price": 16.99, "featured": True},
            {"title": "Fish & Chips",       "description": "Beer-battered cod with fries and tartar.",
            "price": 14.50, "featured": False},
            {"title": "Shrimp Scampi",      "description": "Garlic butter shrimp over linguine.",
            "price": 15.75, "featured": False},
            {"title": "Lobster Roll",       "description": "Chunks of lobster in a toasted brioche roll.",
            "price": 18.50, "featured": False},
            {"title": "Seafood Paella",     "description": "Spanish rice dish with mixed seafood.",
            "price": 17.99, "featured": True},
        ]},
        # 11
        {"title": "Steaks", "slug": "steaks", "items": [
            {"title": "Ribeye Steak",       "description": "12 oz ribeye grilled to perfection.",
            "price": 24.99, "featured": True},
            {"title": "Filet Mignon",       "description": "8 oz tenderloin, center-cut filet.",
            "price": 27.50, "featured": False},
            {"title": "Sirloin Steak",      "description": "10 oz sirloin with herb butter.",
            "price": 21.75, "featured": False},
            {"title": "T-Bone Steak",       "description": "18 oz T-bone served with house sauce.",
            "price": 29.00, "featured": False},
            {"title": "Steak Frites",       "description": "Grilled steak with rosemary fries.",
            "price": 22.99, "featured": True},
        ]},
        # 12
        {"title": "Tacos", "slug": "tacos", "items": [
            {"title": "Al Pastor",          "description": "Marinated pork, pineapple and cilantro.",
            "price": 3.99, "featured": True},
            {"title": "Carne Asada",        "description": "Grilled beef, onions and salsa verde.",
            "price": 4.25, "featured": False},
            {"title": "Fish Taco",          "description": "Baja-style fried fish with cabbage slaw.",
            "price": 4.50, "featured": False},
            {"title": "Shrimp Taco",        "description": "Spicy shrimp with mango pico de gallo.",
            "price": 4.75, "featured": False},
            {"title": "Veggie Taco",        "description": "Roasted veggies, black beans and cheese.",
            "price": 3.75, "featured": True},
        ]},
        # 13
        {"title": "Sushi", "slug": "sushi", "items": [
            {"title": "California Roll",    "description": "Crab, avocado and cucumber roll (8 pcs).",
            "price": 8.99, "featured": True},
            {"title": "Spicy Tuna Roll",    "description": "Tuna with spicy mayo and sesame (8 pcs).",
            "price": 9.50, "featured": False},
            {"title": "Salmon Nigiri",      "description": "Fresh salmon over seasoned rice (2 pcs).",
            "price": 4.25, "featured": False},
            {"title": "Dragon Roll",        "description": "Eel, cucumber roll topped with avocado.",
            "price": 12.00, "featured": False},
            {"title": "Tempura Shrimp Roll","description": "Crispy shrimp tempura roll (8 pcs).",
            "price": 10.50, "featured": True},
        ]},
        # 14
        {"title": "Wraps", "slug": "wraps", "items": [
            {"title": "Chicken Caesar Wrap","description": "Grilled chicken, romaine and Caesar dressing.",
            "price": 8.50, "featured": True},
            {"title": "Falafel Wrap",       "description": "Crispy falafel with hummus and veggies.",
            "price": 7.99, "featured": False},
            {"title": "Turkey Club Wrap",   "description": "Roasted turkey, bacon and avocado.",
            "price": 8.75, "featured": False},
            {"title": "Steak Fajita Wrap",  "description": "Sliced steak, peppers and onions.",
            "price": 9.25, "featured": False},
            {"title": "Veggie Hummus Wrap", "description": "Fresh vegetables with classic hummus.",
            "price": 7.50, "featured": True},
        ]},
        # 15
        {"title": "Smoothies", "slug": "smoothies", "items": [
            {"title": "Berry Blast",        "description": "Blend of strawberries, blueberries and raspberries.",
            "price": 4.99, "featured": True},
            {"title": "Mango Madness",      "description": "Mango, pineapple and orange juice.",
            "price": 4.99, "featured": False},
            {"title": "Green Detox",        "description": "Spinach, kale, apple and banana.",
            "price": 5.25, "featured": False},
            {"title": "Peanut Butter Power","description": "Banana, peanut butter and whey protein.",
            "price": 5.75, "featured": False},
            {"title": "Tropical Sunrise",   "description": "Passionfruit, mango and coconut water.",
            "price": 5.50, "featured": True},
        ]},
        # 16
        {"title": "Coffee", "slug": "coffee", "items": [
            {"title": "Espresso",           "description": "Single shot of rich espresso.",
            "price": 2.50, "featured": True},
            {"title": "Americano",          "description": "Espresso diluted with hot water.",
            "price": 2.75, "featured": False},
            {"title": "Latte",              "description": "Espresso with steamed milk and light foam.",
            "price": 3.50, "featured": False},
            {"title": "Cappuccino",         "description": "Equal parts espresso, steamed milk and foam.",
            "price": 3.50, "featured": False},
            {"title": "Mocha",              "description": "Chocolate latte topped with whipped cream.",
            "price": 3.99, "featured": True},
        ]},
        # 17
        {"title": "Appetizers", "slug": "appetizers", "items": [
            {"title": "Mozzarella Sticks",  "description": "Fried mozzarella served with marinara.",
            "price": 6.99, "featured": True},
            {"title": "Nachos",             "description": "Tortilla chips topped with cheese and jalapeños.",
            "price": 7.50, "featured": False},
            {"title": "Garlic Bread",       "description": "Toasted baguette with garlic butter.",
            "price": 4.25, "featured": False},
            {"title": "Chicken Wings",      "description": "Buffalo or BBQ wings (8 pcs).",
            "price": 8.99, "featured": False},
            {"title": "Spinach Dip",        "description": "Creamy spinach and artichoke dip with chips.",
            "price": 7.25, "featured": True},
        ]},
        # 18
        {"title": "Sides", "slug": "sides", "items": [
            {"title": "French Fries",       "description": "Crispy golden fries seasoned with sea salt.",
            "price": 3.25, "featured": True},
            {"title": "Sweet Potato Fries", "description": "Sweet and crispy fries with paprika.",
            "price": 3.75, "featured": False},
            {"title": "Onion Rings",        "description": "Beer-battered onion rings served hot.",
            "price": 3.99, "featured": False},
            {"title": "Coleslaw",           "description": "Creamy cabbage slaw with carrots.",
            "price": 2.99, "featured": False},
            {"title": "Side Salad",         "description": "Mixed greens with house vinaigrette.",
            "price": 3.50, "featured": True},
        ]},
        # 19
        {"title": "Kids Meals", "slug": "kids-meals", "items": [
            {"title": "Kids Pizza",         "description": "Personal cheese pizza for children.",
            "price": 6.99, "featured": True},
            {"title": "Chicken Nuggets",    "description": "Breaded chicken nuggets with fries.",
            "price": 5.99, "featured": False},
            {"title": "Mini Burger",        "description": "Small beef burger with cheese.",
            "price": 5.75, "featured": False},
            {"title": "Mac & Cheese Bowl",  "description": "Kid-sized portion of mac and cheese.",
            "price": 5.50, "featured": False},
            {"title": "Grilled Cheese",     "description": "Half grilled cheese sandwich.",
            "price": 4.99, "featured": True},
        ]},
        # 20
        {"title": "Vegan", "slug": "vegan", "items": [
            {"title": "Vegan Buddha Bowl",  "description": "Quinoa, chickpeas, roasted veggies and tahini.",
            "price": 10.50, "featured": True},
            {"title": "Vegan Pad Thai",     "description": "Rice noodles with tofu and tamarind sauce.",
            "price": 11.25, "featured": False},
            {"title": "Beyond Burger",      "description": "Plant-based burger with vegan cheese.",
            "price": 12.50, "featured": False},
            {"title": "Vegan Burrito",      "description": "Black beans, rice and guacamole in a tortilla.",
            "price": 9.99, "featured": False},
            {"title": "Vegan Brownie",      "description": "Rich chocolate brownie made dairy-free.",
            "price": 4.75, "featured": True},
        ]},
    ]


    for category_data in categories_data:
        category, _ = Category.objects.get_or_create(
        slug=category_data["slug"],
        defaults={"title": category_data["title"]},
    )

    for item_data in category_data["items"]:
        item, created = MenuItem.objects.get_or_create(
            title=item_data["title"],
            category=category,
            defaults={
                "description": item_data["description"],
                "price": item_data["price"],
                "featured": item_data["featured"],
            },
        )
        # Si el ítem ya existía pero no tenía descripción, la rellenamos
        if not created and not item.description:
            item.description = item_data["description"]
            item.price = item_data["price"]         # opcional: mantén actualizado
            item.featured = item_data["featured"]   # opcional
            item.save(update_fields=["description", "price", "featured"])