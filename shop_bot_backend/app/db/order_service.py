import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.db.product_service import get_db_connection
from decimal import Decimal

def init_order_table():
    """
    Khởi tạo bảng order trong database nếu chưa tồn tại
    Bảng này lưu trữ thông tin về các đơn hàng bao gồm:
    - ID người dùng
    - ID sản phẩm
    - Số lượng
    - Tổng tiền
    - Trạng thái đơn hàng
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS "order" (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    product_id INTEGER NOT NULL REFERENCES product(id),
                    quantity INTEGER NOT NULL,
                    total_amount DECIMAL(10,2) NOT NULL,
                    status VARCHAR(50) NOT NULL DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()


def create_order(user_id: str, product_id: int, quantity: int, total_amount: Decimal) -> dict | None:
    """
    Tạo đơn hàng mới

    Args:
        user_id (str): ID của người dùng
        product_id (int): ID của sản phẩm
        quantity (int): Số lượng sản phẩm
        total_amount (Decimal): Tổng tiền đơn hàng

    Returns:
        dict | None: Thông tin đơn hàng nếu tạo thành công, None nếu thất bại
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO "order" (user_id, product_id, quantity, total_amount)
                VALUES (%s, %s, %s, %s)
                RETURNING 
                    id,
                    user_id,
                    product_id,
                    quantity,
                    total_amount,
                    status,
                    created_at,
                    updated_at
                """,
                (user_id, product_id, quantity, total_amount)
            )
            result = cur.fetchone()
            conn.commit()
            return result


def update_order_status(order_id: int, status: str) -> dict | None:
    """
    Cập nhật trạng thái đơn hàng

    Args:
        order_id (int): ID của đơn hàng
        status (str): Trạng thái mới (pending, confirmed, paid, cancelled)

    Returns:
        dict | None: Thông tin đơn hàng sau khi cập nhật, None nếu thất bại
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE "order"
                SET status = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id
                """,
                (status, order_id)
            )
            result = cur.fetchone()
            conn.commit()
            return bool(result)

if __name__ == '__main__':
    init_order_table()