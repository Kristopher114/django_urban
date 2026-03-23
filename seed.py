import os
import django
from decimal import Decimal

# 1. TURN ON DJANGO FIRST!
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'urban_ordering.settings')
django.setup()

# 2. IMPORT MODELS SECOND! (This must stay below django.setup())
from products.models import Category, Product
def seed_database():
    print("🧹 Clearing old data...")
    Product.objects.all().delete()
    Category.objects.all().delete()

    print("📁 Creating Categories...")
    hot_coffee = Category.objects.create(name="Hot Coffee", description="Freshly brewed hot espresso beverages.")
    iced_coffee = Category.objects.create(name="Iced Coffee", description="Refreshing cold coffee over ice.")
    frappes = Category.objects.create(name="Frappes & Blended", description="Ice-blended sweet coffee and cream drinks.")
    tea_matcha = Category.objects.create(name="Tea & Matcha", description="Premium steeped teas and authentic Japanese matcha.")
    pastries = Category.objects.create(name="Pastries & Sweets", description="Freshly baked daily treats and cakes.")
    savory = Category.objects.create(name="Savory Sandwiches", description="Hot, toasted sandwiches for a quick bite.")

    print("☕ Stocking the shelves with products...")
    products_data = [
        # --- HOT COFFEE ---
        {"name": "Classic Espresso", "desc": "A strong, bold double shot of our signature dark roast.", "price": "100.00", "stock": 100, "cat": hot_coffee},
        {"name": "Americano", "desc": "Rich espresso topped with hot water.", "price": "110.00", "stock": 100, "cat": hot_coffee},
        {"name": "Cappuccino", "desc": "Dark, rich espresso lying in wait under a smoothed and stretched layer of thick milk foam.", "price": "140.00", "stock": 80, "cat": hot_coffee},
        {"name": "Cafe Mocha", "desc": "Espresso with bittersweet mocha sauce and steamed milk.", "price": "155.00", "stock": 60, "cat": hot_coffee},
        {"name": "Caramel Macchiato", "desc": "Espresso mixed with steamed milk and sweet caramel drizzle.", "price": "160.00", "stock": 50, "cat": hot_coffee},
        
        # --- ICED COFFEE ---
        {"name": "Iced Americano", "desc": "Espresso shots topped with cold water produce a light layer of crema, then served over ice.", "price": "120.00", "stock": 100, "cat": iced_coffee},
        {"name": "Iced Vanilla Latte", "desc": "Our signature espresso poured over ice with vanilla syrup and milk.", "price": "150.00", "stock": 80, "cat": iced_coffee},
        {"name": "Iced Spanish Latte", "desc": "A sweet, creamy blend of espresso, regular milk, and sweetened condensed milk.", "price": "170.00", "stock": 75, "cat": iced_coffee},
        {"name": "Cold Brew", "desc": "Slow-steeped for 20 hours for a super smooth, less acidic flavor.", "price": "145.00", "stock": 40, "cat": iced_coffee},

        # --- FRAPPES & BLENDED ---
        {"name": "Java Chip Frappe", "desc": "Mocha sauce and Frappuccino chips blended with coffee, milk and ice.", "price": "190.00", "stock": 50, "cat": frappes},
        {"name": "Caramel Frappe", "desc": "Caramel syrup meets coffee, milk and ice for a rendezvous in the blender.", "price": "185.00", "stock": 50, "cat": frappes},
        {"name": "Cookies & Cream Frappe", "desc": "A cream-based blend of chocolate cookies and milk, topped with whipped cream. (Coffee-free)", "price": "180.00", "stock": 60, "cat": frappes},

        # --- TEA & MATCHA ---
        {"name": "Iced Matcha Latte", "desc": "Premium grade matcha green tea shaken with milk and ice.", "price": "160.00", "stock": 60, "cat": tea_matcha},
        {"name": "Hot Earl Grey Tea", "desc": "A robust black tea with rich citrusy notes of bergamot.", "price": "110.00", "stock": 90, "cat": tea_matcha},
        {"name": "Peach Iced Tea", "desc": "Refreshing black tea infused with sweet peach syrup.", "price": "130.00", "stock": 80, "cat": tea_matcha},

        # --- PASTRIES & SWEETS ---
        {"name": "Butter Croissant", "desc": "Flaky, buttery, and baked fresh every single morning.", "price": "85.00", "stock": 30, "cat": pastries},
        {"name": "Blueberry Muffin", "desc": "Soft muffin loaded with real blueberries and a crumb topping.", "price": "95.00", "stock": 25, "cat": pastries},
        {"name": "Dark Chocolate Chip Cookie", "desc": "Chewy on the inside, crispy on the outside, loaded with dark chocolate chunks.", "price": "75.00", "stock": 40, "cat": pastries},
        {"name": "New York Cheesecake", "desc": "A rich, creamy slice of classic cheesecake with a graham cracker crust.", "price": "165.00", "stock": 15, "cat": pastries},

        # --- SAVORY SANDWICHES ---
        {"name": "Ham & Cheese Croissant", "desc": "Our classic butter croissant sliced and filled with smoked ham and melted cheddar.", "price": "140.00", "stock": 20, "cat": savory},
        {"name": "Pesto Chicken Sandwich", "desc": "Grilled chicken breast, mozzarella, and basil pesto panini pressed to perfection.", "price": "180.00", "stock": 15, "cat": savory},
        {"name": "Three-Cheese Grilled Cheese", "desc": "Cheddar, mozzarella, and gouda melted between thick-cut sourdough bread.", "price": "150.00", "stock": 20, "cat": savory},
    ]

    for item in products_data:
        Product.objects.create(
            name=item["name"],
            description=item["desc"],
            price=Decimal(item["price"]),
            stock_quantity=item["stock"],
            category=item["cat"]
        )

    print(f"✅ Successfully seeded {len(products_data)} products across {Category.objects.count()} categories!")

    # --- ADD THESE TWO LINES AT THE VERY BOTTOM ---
if __name__ == '__main__':
    seed_database()