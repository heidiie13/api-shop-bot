import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.db.product_service import get_db_connection
from decimal import Decimal

def init_wallet_table():
    """
    Initialize user_wallet table in database if not exists
    This table stores information about user's wallet, including:
    - User ID
    - Balance
    - Created and updated time
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_wallet (
                    id SERIAL PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL UNIQUE,
                    balance DECIMAL(15,2) NOT NULL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        conn.commit()

def get_wallet(user_id: str) -> dict | None:
    """
    Lấy thông tin ví của người dùng
    
    Args:
        user_id (str): ID của người dùng
        
    Returns:
        dict | None: Thông tin ví nếu tìm thấy, None nếu không tìm thấy
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    id,
                    user_id,
                    balance,
                    created_at,
                    updated_at
                FROM user_wallet 
                WHERE user_id = %s
                """,
                (user_id,)
            )
            result = cur.fetchone()
            return result

def create_wallet(user_id: str, initial_balance: Decimal = Decimal('0')) -> dict | None:
    """
    Tạo ví mới cho người dùng
    
    Args:
        user_id (str): ID của người dùng
        initial_balance (Decimal): Số dư ban đầu, mặc định là 0
        
    Returns:
        dict | None: Thông tin ví nếu tạo thành công, None nếu thất bại
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT user_id FROM user_wallet WHERE user_id = %s
                """,(user_id,)
            )
            exist = cur.fetchone()
            if exist:
                cur.execute(
                    """
                    UPDATE user_wallet 
                    SET balance = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = %s
                    RETURNING user_id, balance
                    """, (initial_balance, user_id)
                )
            else:
                cur.execute(
                    """
                    INSERT INTO user_wallet (user_id, balance)
                    VALUES (%s, %s)
                    RETURNING user_id, balance
                    """,
                    (user_id, initial_balance)
                )
                
            result = cur.fetchone()
            conn.commit()
            return result

def update_balance(user_id: str, amount: Decimal) -> dict | None:
    """
    Cập nhật số dư trong ví của người dùng
    
    Args:
        user_id (str): ID của người dùng
        amount (Decimal): Số tiền cần thay đổi (dương để thêm vào, âm để trừ đi)
        
    Returns:
        dict | None: Thông tin ví sau khi cập nhật, None nếu thất bại hoặc số dư không đủ
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE user_wallet
                SET balance = balance + %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND balance + %s >= 0
                RETURNING 
                    id,
                    user_id,
                    balance,
                    created_at,
                    updated_at
                """,
                (amount, user_id, amount)
            )
            result = cur.fetchone()
            conn.commit()
            return result 
        
if __name__ == '__main__':
    init_wallet_table()