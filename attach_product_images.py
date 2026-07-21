import os
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product

MEDIA_PRODUCTS_DIR = os.path.join(os.path.dirname(__file__), 'media', 'products')
os.makedirs(MEDIA_PRODUCTS_DIR, exist_ok=True)

ARTIFACTS_DIR = r"C:\Users\ganes\.gemini\antigravity-ide\brain\67dd530d-a95f-49fd-8b0d-0fc1216ac47e"

image_mappings = {
    "iPhone 15 Pro": "iphone_15_pro_1784613787796.png",
    "MacBook Pro 14\"": "macbook_pro_14_1784613808761.png",
    "Sony WH-1000XM5": "sony_wh1000xm5_1784613827600.png",
    "iPad Air 10.9\"": "ipad_air_1784613847989.png",
    "Apple Watch Series 9": "apple_watch_series_9_1784613864657.png",
    "PlayStation 5 Console": "ps5_console_1784613883224.png",
}

for product_name, artifact_filename in image_mappings.items():
    src_path = os.path.join(ARTIFACTS_DIR, artifact_filename)
    if os.path.exists(src_path):
        target_filename = artifact_filename.split('_1784')[0] + '.png'
        dst_path = os.path.join(MEDIA_PRODUCTS_DIR, target_filename)
        shutil.copy2(src_path, dst_path)
        print(f"Copied {artifact_filename} -> {dst_path}")
        
        product = Product.objects.filter(name=product_name).first()
        if product:
            product.image = f"products/{target_filename}"
            product.save()
            print(f"Updated product '{product.name}' image to products/{target_filename}")
        else:
            print(f"Product '{product_name}' not found in database.")
    else:
        print(f"Source file {src_path} not found.")

print("All product images attached successfully!")
