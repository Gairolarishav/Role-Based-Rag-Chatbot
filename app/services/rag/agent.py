from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from langchain_community.vectorstores import FAISS
from langchain_core.tools import tool
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain.messages import HumanMessage,AIMessage,ToolMessage
import json

load_dotenv()

faiss_path = r"E:\Gen AI Roadmap\Gen AI Projects\Rolebased_AI_Chatbot_fintech\ds-rpc-01\faiss_index"

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vector_store = FAISS.load_local(
    faiss_path, embedding_model, allow_dangerous_deserialization=True
)

# -----------------------------
# Request & Response Schemas
# -----------------------------
class ChatRequest(BaseModel):
    user_query: str
    user_role: str = "engineering"


@tool("rag_tool", description="Retrieves relevant documents based on user role and user query")
def rag_tool(query:str,user_role:str):
    print(f"🔍 RAG Tool invoked for role: {user_role} and query: {query}")
    try:
        # Document retrieval based on role
        if "c-levelexecutives" in user_role:
            retrieved_docs = vector_store.similarity_search(
                query, k=5,
                filter={"category": {"$in": ["engineering", "hr", "finance", "marketing", "general"]}}
            )
        elif "employee" in user_role:
            retrieved_docs = vector_store.similarity_search(query, k=3, filter={"category": "general"})
        else:
            retrieved_docs = vector_store.similarity_search(query, k=3, filter={"category": user_role})

        context_chunks = []
        sources = []

        for doc in retrieved_docs:
            context_chunks.append(doc.page_content)

            sources.append({
                "source": doc.metadata.get("source"),
            })

        return {
            "context": "\n\n".join(context_chunks),
            "sources": sources
        }

    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        return {
            "context": "",
            "sources": []
        }
    

def extract_text(content):
    """
    Normalizes AIMessage.content to plain string
    """
    # Case 1: already a string
    if isinstance(content, str):
        return content

    # Case 2: list of blocks
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block.get("text", ""))
        return " ".join(texts)

    # Fallback
    return str(content)

# Streaming chat endpoint
def query(message,user_role):
    """
    Streaming endpoint that sends response chunks as Server-Sent Events (SSE)
    """

    agent = create_agent(llm,tools=[rag_tool],system_prompt=f"""You are an AI assistant at FinSolve Technologies.call rag_tool when need with:
    - user_role = {user_role}

    Use the retrieved context to answer accurately.""")


    result  = agent.invoke(
        {"messages": [HumanMessage(message)]}
    )

    tool_used = False
    tool_name = None
    final_answer = None
    sources = []

    for msg in result["messages"]:

        # Tool was called
        if isinstance(msg, AIMessage) and msg.tool_calls:
            tool_used = True
            tool_name = msg.tool_calls[0]["name"]

        # Tool returned data
        if isinstance(msg, ToolMessage):
            try:
                tool_data = json.loads(msg.content)
                sources = tool_data.get("sources", [])
            except Exception:
                sources = []

        # Final AI answer
        if isinstance(msg, AIMessage) and not msg.tool_calls:
            final_answer = extract_text(msg.content)


    return tool_used,tool_name,final_answer,sources
