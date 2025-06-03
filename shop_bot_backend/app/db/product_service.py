import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv(override=True)

DB_NAME = os.getenv('DB_NAME')
DB_USERNAME = os.getenv('DB_USERNAME')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

def get_db_connection():
    """
    Connect to PostgreSQL database
    
    Returns:
        Connection: Connection to PostgreSQL database
    
    Raises:
        Exception: If connection to database fails
    """
    try:
        conn = psycopg.connect(
            dbname=DB_NAME,
            user=DB_USERNAME,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            row_factory=dict_row
        )
        return conn
    except Exception as e:
        raise RuntimeError(f"Error connecting to PostgreSQL: {e}")
    
def init_product_table():
    """
    Initialize product table in database if not exists
    Product table:
    - Product name
    - Description
    - Price
    - Stock
    - Specifications
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS product (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(255) NOT NULL,
                            description TEXT,
                            price DECIMAL(10, 2) NOT NULL,
                            stock INTEGER NOT NULL DEFAULT 0,
                            specifications JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """)
        conn.commit()
        
def get_product_by_name(name: str) -> dict | None:
    """
    Query product by name

    Args:
        name (str): The name of the product to search for

    Returns:
        dict | None: Product information if found, None if not found
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT
                            id,
                            name,
                            description,
                            price,
                            stock,
                            specifications,
                            created_at,
                            updated_at
                        FROM product
                        WHERE LOWER(name) LIKE LOWER(%s)
                        """,
                        (name,))
            result = cur.fetchone()

            return result

def check_product_stock(product_id: int, quantity: int) -> bool:
    """
    Check the stock of a product

    Args:
        product_id (int): ID of the product
        quantity (int): The quantity to check

    Returns:
        bool: True if the stock is >= the quantity to check, False if not enough
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        SELECT stock
                        FROM product
                        WHERE id = %s
                        """,
                        (product_id,))
            result = cur.fetchone()

            return result and result['stock'] >= quantity
        
        
def update_product_stock(product_id: int, quantity: int):
    """
    Update the stock of a product

    Args:
        product_id (int): ID of the product
        quantity (int): The quantity to update (negative to add to stock)
    
    Returns:
        bool: True if update is successful, False if fails
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        UPDATE product
                        SET stock = stock - %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s AND stock >= %s
                        RETURNING id
                        """,
                        (quantity, product_id, quantity))
            result = cur.fetchone()
            conn.commit()
            
            return bool(result)
        

def main():
    init_product_table()
    print(get_product_by_name("iPhone 16 pro Max"))
    
if __name__ == '__main__':
    main()