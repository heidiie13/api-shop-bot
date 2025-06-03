import sys, os
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from typing import AsyncGenerator
from dotenv import load_dotenv
from app.core_ai.tools import ProductSearchTool, CreateOrderTool, UpdateOrderStatusTool
from app.core_ai.prompts import system_prompt
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks.base import BaseCallbackHandler

from app.db.chat_history_service import get_recent_chat_history, save_chat_history

load_dotenv(override=True)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GOOGLE_MODEL_NAME", "gemini-pro")

if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables")

product_search_tool = ProductSearchTool()
create_order_tool = CreateOrderTool()
update_order_status_tool = UpdateOrderStatusTool()

def get_llm_and_agent() -> AgentExecutor:
    chat = ChatGoogleGenerativeAI(
        model=MODEL_NAME,
        google_api_key=GOOGLE_API_KEY,
        temperature=0,
        # convert_system_message_to_human=True,
        # streaming=True
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
        verbose=True,
        return_intermediate_steps=True
    )

    return agent_executor

def format_chat_history(history: list) -> list:
    """Format chat history into a list of message tuples"""
    formatted_history = []
    for msg in reversed(history):
        formatted_history.extend([
            ("human", msg["question"]),
            ("assistant", msg["answer"])
        ])
    return formatted_history

def get_answer(question: str, thread_id: str) -> dict:
    """
    Get answer for a question
    
    Args:
        question (str): Question from user
        thread_id (str): ID of the conversation
        
    Returns:
        dict: Answer from AI
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
    Get answer for a question in stream format
    
    Args:
        question (str): Question from user
        thread_id (str): ID of the conversation
        
    Returns:
        AsyncGenerator[str, None]: Generator that yields each part of the answer
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
        async for event in get_answer_stream("tôi muốn mua 1 cái Xiaomi 14 Pro", "3"):
            print(event)
    
    asyncio.run(test())