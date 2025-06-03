from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chatbot.routes import router as chat_router
from app.db.chat_history_service import init_chat_history_table
from app.db.product_service import init_product_table
from app.db.order_service import init_order_table
from app.db.wallet_service import init_wallet_table

app = FastAPI()

# Initialize database tables
@app.on_event("startup")
async def startup_event():
    """Initialize all database tables on startup"""
    init_product_table()
    init_order_table()
    init_wallet_table()
    init_chat_history_table()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")