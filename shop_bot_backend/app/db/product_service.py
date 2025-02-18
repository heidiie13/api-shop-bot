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
    Tạo kết nối với database PostgreSQL
    
    Returns:
        Connection: Kết nối với database PostgreSQL
    
    Raises:
        Exception: Nếu không thể kết nối đến database
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
    Khởi tạo bảng product trong db nếu chưa tồn tại
    Bảng product:
    - Tên sản phẩm
    - Mô tả
    - Giá
    - Số lượng tồn kho
    - Thông số kỹ thuật
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
    Truy vấn product bằng tên

    Args:
        name (str): Tên sản phẩm cần tìm

    Returns:
        dict | None: Thông tin sản phẩm nếu có, None nếu không tìm thấy
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
    Kiểm tra số lượng tồn kho của sản phẩm

    Args:
        product_id (int): ID sản phẩm
        quantity (int): Số lượng cần kiểm tra

    Returns:
        bool: True nếu số lượng tồn kho >= số lượng cần kiểm tra, False nếu không đủ
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
    Cập nhật số lượng tồn kho của sản phẩm

    Args:
        product_id (int): ID sản phẩm
        quantity (int): Số lượng cần cập nhật (số âm để thêm số lượng tồn kho)
    
    Returns:
        bool: True nếu cập nhật thành công, False nếu thất bại
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