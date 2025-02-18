import json
from decimal import Decimal

from product_service import init_product_table, get_db_connection
from order_service import init_order_table
from wallet_service import init_wallet_table, create_wallet


SAMPLE_PRODUCTS = [
    {
        "name": "iPhone 16 Pro Max",
        "description": "iPhone 16 Pro Max mới nhất với nhiều tính năng đột phá",
        "price": 35990000,
        "stock": 50,
        "specifications": {
            "màn_hình": "6.9 inch OLED ProMotion 144Hz",
            "chip": "A18 Bionic",
            "ram": "12GB",
            "bộ_nhớ": "1TB",
            "camera": "108MP + 48MP + 12MP",
            "pin": "5000mAh",
            "sạc": "45W",
            "màu_sắc": ["Titan Đen", "Titan Trắng", "Titan Vàng", "Titan Xanh"]
        }
    },
    {
        "name": "Samsung Galaxy S24 Ultra",
        "description": "Samsung Galaxy S24 Ultra với bút S-Pen và camera zoom 100x",
        "price": 31990000,
        "stock": 40,
        "specifications": {
            "màn_hình": "6.8 inch Dynamic AMOLED 2X 120Hz",
            "chip": "Snapdragon 8 Gen 3",
            "ram": "12GB",
            "bộ_nhớ": "512GB",
            "camera": "200MP + 50MP + 12MP + 10MP",
            "pin": "5000mAh",
            "sạc": "45W",
            "màu_sắc": ["Đen", "Cream", "Violet", "Xanh"]
        }
    },
    {
        "name": "Xiaomi 14 Pro",
        "description": "Xiaomi 14 Pro với camera Leica và sạc siêu nhanh",
        "price": 22990000,
        "stock": 60,
        "specifications": {
            "màn_hình": "6.7 inch AMOLED 120Hz",
            "chip": "Snapdragon 8 Gen 3",
            "ram": "12GB",
            "bộ_nhớ": "256GB",
            "camera": "50MP + 50MP + 50MP",
            "pin": "4800mAh",
            "sạc": "120W",
            "màu_sắc": ["Đen", "Trắng", "Xanh"]
        }
    },
    {
        "name": "OPPO Find X7 Ultra",
        "description": "OPPO Find X7 Ultra với camera Hasselblad",
        "price": 24990000,
        "stock": 45,
        "specifications": {
            "màn_hình": "6.8 inch AMOLED 120Hz",
            "chip": "Dimensity 9300",
            "ram": "16GB",
            "bộ_nhớ": "512GB",
            "camera": "50MP + 50MP + 50MP + 50MP",
            "pin": "5000mAh",
            "sạc": "100W",
            "màu_sắc": ["Đen", "Bạc", "Xanh"]
        }
    },
    {
        "name": "Google Pixel 8 Pro",
        "description": "Google Pixel 8 Pro với AI và camera đỉnh cao",
        "price": 25990000,
        "stock": 35,
        "specifications": {
            "màn_hình": "6.7 inch LTPO OLED 120Hz",
            "chip": "Google Tensor G3",
            "ram": "12GB",
            "bộ_nhớ": "256GB",
            "camera": "50MP + 48MP + 48MP",
            "pin": "5000mAh",
            "sạc": "30W",
            "màu_sắc": ["Obsidian", "Bay", "Porcelain"]
        }
    }
]

SAMPLE_USERS = [
    {
        "user_id": "user1",
        "balance": Decimal("200000000")
    },
    {
        "user_id": "user2",
        "balance": Decimal("150000000")
    },
    {
        "user_id": "user3",
        "balance": Decimal("300000000")
    }
]

def seed_products():
    """Seed products into database"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE product CASCADE")
            
            for product in SAMPLE_PRODUCTS:
                cur.execute(
                    """
                    INSERT INTO product (name, description, price, stock, specifications)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        product["name"],
                        product["description"],
                        product["price"],
                        product["stock"],
                        json.dumps(product["specifications"])
                    )
                )
        conn.commit()

def seed_wallets():
    """Seed user wallets into database"""
    for user in SAMPLE_USERS:
        create_wallet(user["user_id"], user["balance"])

def init_and_seed_database():
    """Initialize tables and seed data"""
    print("Initializing tables...")
    init_product_table()
    init_order_table()
    init_wallet_table()
    
    print("Seeding products...")
    seed_products()
    
    print("Seeding user wallets...")
    seed_wallets()
    
    print("Database initialization and seeding completed!")

if __name__ == "__main__":
    init_and_seed_database() 