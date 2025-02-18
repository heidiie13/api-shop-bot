

import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from typing import AsyncGenerator
from dotenv import load_dotenv
from app.core_ai.tools import ProductSearchTool, CreateOrderTool, UpdateOrderStatusTool
from app.core_ai.prompts import system_prompt
from langchain_openai import ChatOpenAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler

from app.db.chat_history_service import get_recent_chat_history, save_chat_history, format_chat_history
import certifi, ssl, httpx
os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv(override=True)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")


if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

product_search_tool = ProductSearchTool()
create_order_tool = CreateOrderTool()
update_order_status_tool = UpdateOrderStatusTool()

def get_llm_and_agent() -> AgentExecutor:
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    http_client = httpx.Client(verify=ssl_context)
    
    chat = ChatOpenAI(
        model=MODEL_NAME, 
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
        temperature=0, 
        streaming=True, 
        http_client= http_client,
        callbacks=[BaseCallbackHandler()]
        )
    
    tools = [
        product_search_tool,
        create_order_tool,
        update_order_status_tool
    ]

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(
        llm=chat,
        tools=tools,
        prompt=prompt
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=False,
        return_intermediate_steps=True
    )

    return agent_executor

def get_answer(question: str, thread_id: str) -> dict:
    """
    Hàm lấy câu trả lời cho một câu hỏi
    
    Args:
        question (str): Câu hỏi của người dùng
        thread_id (str): ID của cuộc trò chuyện
        
    Returns:
        dict: Câu trả lời từ AI
    """
    agent = get_llm_and_agent()
    
    history = get_recent_chat_history(thread_id)
    chat_history = format_chat_history(history)
    
    result = agent.invoke({
        "input": question,
        "chat_history": chat_history
    })
    
    if isinstance(result, dict) and "output" in result:
        save_chat_history(thread_id, question, result["output"])
    
    return result

async def get_answer_stream(question: str, thread_id: str) -> AsyncGenerator[str, None]:
    """
    Hàm lấy câu trả lời dạng stream cho một câu hỏi
    
    Args:
        question (str): Câu hỏi của người dùng
        thread_id (str): ID phiên chat
        
    Returns:
        AsyncGenerator[str, None]: Generator trả về từng phần của câu trả lời
    """
    agent = get_llm_and_agent()
    
    history = get_recent_chat_history(thread_id)
    chat_history = format_chat_history(history)
    
    final_answer = ""
    
    async for event in agent.astream_events(
        {
            "input": question,
            "chat_history": chat_history,
        },
        version="v2"
    ):       
        kind = event["event"]
        if kind == "on_chat_model_stream":
            content = event['data']['chunk'].content
            if content:
                final_answer += content
                yield content
    
    if final_answer:
        save_chat_history(thread_id, question, final_answer)

if __name__ == "__main__":
    import asyncio
    
    async def test():
        async for event in get_answer_stream("Tôi là user_2, tôi xác nhận đã thanh toán rồi,order_id là 2", "test-session-100"):
            print(event)
        print('done')

    
    asyncio.run(test())