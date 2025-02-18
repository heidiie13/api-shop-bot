import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.db.product_service import get_db_connection
def init_chat_history_table():
    """
    Khởi tạo bảng message trong database nếu chưa tồn tại
    Bảng này lưu trữ lịch sử chat bao gồm:
    - ID tin nhắn (UUID)
    - ID cuộc trò chuyện
    - Câu hỏi
    - Câu trả lời
    - Thời gian tạo
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS message (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    thread_id VARCHAR(255) NOT NULL,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_message_thread_id 
                ON message(thread_id)
            """)
        conn.commit()

def save_chat_history(thread_id: str, question: str, answer: str) -> dict:
    """
    Lưu lịch sử chat vào database
    
    Args:
        thread_id (str): ID của cuộc trò chuyện
        question (str): Câu hỏi của người dùng
        answer (str): Câu trả lời của chatbot
        
    Returns:
        dict: Thông tin lịch sử chat vừa được lưu
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO message (thread_id, question, answer) VALUES (%s, %s, %s) RETURNING id::text",
                (thread_id, question, answer)
            )
            result = cur.fetchone()
        conn.commit()
        return result['id']

def get_recent_chat_history(thread_id: str, limit: int = 10) -> list[dict]:
    """
    Lấy lịch sử chat gần đây của một cuộc trò chuyện
    
    Args:
        thread_id (str): ID của cuộc trò chuyện
        limit (int): Số lượng tin nhắn tối đa cần lấy, mặc định là 10
        
    Returns:
        list[dict]: Danh sách các tin nhắn gần đây
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    id::text,
                    thread_id,
                    question,
                    answer,
                    created_at
                FROM message 
                WHERE thread_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
                """,
                (thread_id, limit)
            )
            return cur.fetchall()

def format_chat_history(chat_history: list[dict]) -> str:
    """
    Định dạng lịch sử chat thành chuỗi văn bản
    
    Args:
        chat_history (list[dict]): Danh sách các tin nhắn
        
    Returns:
        str: Chuỗi văn bản đã được định dạng
    """
    formatted_history = []
    for msg in reversed(chat_history):
        formatted_history.extend([
            {"role": "human", "content": msg["question"]},
            {"role": "assistant", "content": msg["answer"]}
        ])
    return formatted_history

def main():
    init_chat_history_table() 
    
if __name__ == '__main__':
    main()