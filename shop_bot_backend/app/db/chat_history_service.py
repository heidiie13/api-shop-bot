import sys, os
import logging

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app.db.product_service import get_db_connection

logger = logging.getLogger(__name__)

def init_chat_history_table():
    """
    Initialize the message table in the database if it does not exist.
    This table stores chat history including:
    - Message ID (UUID)
    - Conversation ID
    - Question
    - Answer
    - Creation time
    """
    try:
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
            logger.info("Chat history table initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing chat history table: {e}")
        raise

def save_chat_history(thread_id: str, question: str, answer: str) -> dict:
    """
    Save chat history to database
    
    Args:
        thread_id (str): ID of the conversation
        question (str): User's question
        answer (str): Chatbot's answer
        
    Returns:
        dict: Information about the saved chat history
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO message (thread_id, question, answer) VALUES (%s, %s, %s) RETURNING id::text",
                    (thread_id, question, answer)
                )
                result = cur.fetchone()
            conn.commit()
            return result['id']
    except Exception as e:
        logger.error(f"Error saving chat history: {e}")
        raise

def get_recent_chat_history(thread_id: str, limit: int = 10) -> list[dict]:
    """
    Retrieve recent chat history for a conversation
    
    Args:
        thread_id (str): ID of the conversation
        limit (int): Maximum number of messages to retrieve, default is 10
        
    Returns:
        list[dict]: List of recent messages
    """
    try:
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
                return cur.fetchall() or []
    except Exception as e:
        logger.error(f"Error getting chat history: {e}")
        return []

def main():
    init_chat_history_table() 
    
if __name__ == '__main__':
    main()