import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product

def seed():
    print("Seeding database with premium products...")
    
    # Clear existing products to avoid duplicates
    Product.objects.all().delete()
    
    products_data = [
        {
            "name": "iPhone 15 Pro",
            "description": "Forged in titanium and featuring the groundbreaking A17 Pro chip, a customizable Action button, and the most powerful iPhone camera system ever.",
            "price": 999.99,
            "stock": 10,
            "image": "products/iphone_15_pro.png"
        },
        {
            "name": "MacBook Pro 14\"",
            "description": "Supercharged by the M3 chip. Featuring a stunning Liquid Retina XDR display, up to 22 hours of battery life, and pro-level ports for absolute productivity.",
            "price": 1599.99,
            "stock": 5,
            "image": "products/macbook_pro_14.png"
        },
        {
            "name": "Sony WH-1000XM5",
            "description": "Industry-leading noise cancellation headphones with magnificent sound quality, crystal-clear hands-free calling, and up to 30 hours of continuous wireless playback.",
            "price": 349.99,
            "stock": 15,
            "image": "products/sony_wh1000xm5.png"
        },
        {
            "name": "iPad Air 10.9\"",
            "description": "Powered by the Apple M1 chip. Liquid Retina display, 12MP front camera with Center Stage, super-fast Wi-Fi 6, and support for Apple Pencil (2nd gen).",
            "price": 599.99,
            "stock": 8,
            "image": "products/ipad_air.png"
        },
        {
            "name": "Apple Watch Series 9",
            "description": "Smarter, brighter, and faster. Features a double-tap gesture command, temperature sensing, blood oxygen monitoring, and advanced fitness metrics tracking.",
            "price": 399.99,
            "stock": 12,
            "image": "products/apple_watch_series_9.png"
        },
        {
            "name": "PlayStation 5 Console",
            "description": "Experience lightning-fast loading speeds with an ultra-high speed SSD, deeper immersion with haptic feedback support, adaptive triggers, and 3D Audio technology.",
            "price": 499.99,
            "stock": 7,
            "image": "products/ps5_console.png"
        }
    ]
    
    for item in products_data:
        p = Product.objects.create(
            name=item["name"],
            description=item["description"],
            price=item["price"],
            stock=item["stock"],
            image=item.get("image")
        )
        print(f"Created Product: {p.name}")

    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
