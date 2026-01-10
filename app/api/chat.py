from fastapi import APIRouter, HTTPException
from schemas.chat import ChatRequest
from services.rag.agent import query

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/")
def chat(data: ChatRequest):
    if data:
        message = data.user_query
        user_role = data.user_role.lower()

    tool_used,tool_name,final_answer,sources = query(message, user_role)

    print("sources:", sources)

    response = {
        "tool_used": tool_used,
        "tool_name": tool_name,
        "answer": final_answer,
        "sources": sources
    }

    return response
