"""
embed_documents.py
-------------------
This script loads documents from department folders, splits them into smaller chunks,
generates embeddings using SentenceTransformer, and saves them in a Chroma vector database
with department-level role metadata.
For FinSolve Technologies RAG-based chatbot project.
"""

import os
import shutil
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader, TextLoader,PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv  
from pathlib import Path
from typing import Optional
import tempfile
import json

load_dotenv()

# -------------------------------
# Configuration
# -------------------------------
# BASE_DIR = Path(
#     r"E:\Gen AI Roadmap\Gen AI Projects\Rolebased_AI_Chatbot_fintech\ds-rpc-01\resources\data"
# )

# embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# # -------------------------------
# # Aggregate all split documents
# # -------------------------------
# all_split_docs = []

# for department in os.listdir(BASE_DIR):
#     dept_path = os.path.join(BASE_DIR, department)

#     if os.path.isdir(dept_path):
#         print(f"\n🔍 Processing department: {department}")
#         all_docs = []

#         for file in os.listdir(dept_path):
#             print('file====',file)
#             file_path = os.path.join(dept_path, file)

#             try:
#                 if file.endswith(".md"):
#                     try:
#                         loader = UnstructuredMarkdownLoader(file_path, mode="elements",strategy="fast",)
#                         docs = loader.load()
#                     except:
#                         loader = TextLoader(file_path)
#                         docs = loader.load()
#                 elif file.endswith(".csv"):
#                     loader = CSVLoader(file_path)
#                     docs = loader.load()
#                 else:
#                     continue

#                 all_docs.extend(docs)

#             except Exception as e:
#                 print(f"❌ Failed to load {file}: {e}")

#         if not all_docs:
#             print(f"⚠️ No documents found for department: {department}")
#             continue

#         # Split into chunks and tag with metadata
#         splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
#         split_docs = splitter.split_documents(all_docs)
#         for doc in split_docs:
#             doc.metadata = {    # e.g. "engineering"
#                 "category": "general" if department.lower() == "general" else department.lower(),
#                 "source": file,
#             }

#         all_split_docs.extend(split_docs)
#         print(f"✅ Loaded & split {len(split_docs)} documents for {department}")

# # -------------------------------
# # Build or refresh FAISS DB
# # -------------------------------
# shutil.rmtree('faiss_index', ignore_errors=True)

# # Create FAISS database from already split documents
# db = FAISS.from_documents(
#     documents=all_split_docs,  # Use the already split documents
#     embedding=embedding_model
# )

# # Save the database
# faiss_path = r"E:\Gen AI Roadmap\Gen AI Projects\Rolebased_AI_Chatbot_fintech\ds-rpc-01\faiss_index"
# db.save_local(faiss_path)

# # Create retriever
# retriever = db.as_retriever(search_kwargs={"k": 5})

# print("\n🔍 Testing retrieval:")
# results = retriever.invoke("API Gateway")
# print(f"Retrieved {len(results)} documents")
# if results:
#     print(f"Sample result: {results[0].page_content[:200]}...")

# # -------------------------------
# # Summary
# # -------------------------------
# print(f"\n🎉 Successfully stored {len(all_split_docs)} documents in FAISS.")

FAISS_PATH = "faiss_index"
ROLE_ID_FILE = os.path.join(FAISS_PATH, "role_doc_ids.json")
embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def load_role_doc_ids():
    if os.path.exists(ROLE_ID_FILE):
        with open(ROLE_ID_FILE, "r") as f:
            return json.load(f)
    return {}

def save_role_doc_ids(data):
    os.makedirs(FAISS_PATH, exist_ok=True)
    with open(ROLE_ID_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create_embeddings(role, file_bytes: bytes, filename: Optional[str] = None):
    
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")
    
    temp_path = None
    
    try:
        # 1️⃣ Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name
        
        # 2️⃣ Load and split PDF
        loader = PyPDFLoader(temp_path)
        docs = loader.load()
        
        if not docs:
            raise ValueError("No content extracted from PDF")

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(docs)

        # 3️⃣ Create IDs and update metadata
        new_ids = []
        
        for index, doc in enumerate(split_docs, start=1):
            doc.metadata = {
                "source": filename if filename else "unknown",
                "category": role.lower()
            }
            new_ids.append(f"{role.lower()}_{index}")  # Fixed: removed space, added .lower()

        # 4️⃣ Load or create FAISS
        if os.path.exists(os.path.join(FAISS_PATH, "index.faiss")):  # Fixed: check for actual index file
            print("Loading existing FAISS index...")
            vector_store = FAISS.load_local(
                FAISS_PATH,
                embedding_model,
                allow_dangerous_deserialization=True
            )
        else:
            print("Creating new FAISS index...")
            os.makedirs(FAISS_PATH, exist_ok=True)
            # Create initial vector store with first documents
            vector_store = FAISS.from_documents(
                documents=split_docs,
                embedding=embedding_model,
                ids=new_ids
            )
            # Save mapping and index
            role_doc_ids = {role: new_ids}
            save_role_doc_ids(role_doc_ids)
            vector_store.save_local(FAISS_PATH)
            
            response = f"✅ Embeddings created for role: {role} ({len(split_docs)} chunks)"
            return response
        
        # 5️⃣ Role-based delete (only for existing index)
        role_doc_ids = load_role_doc_ids()
        if role in role_doc_ids:
            old_ids = role_doc_ids[role]
            print(f"Deleting {len(old_ids)} old embeddings for role: {role}")
            vector_store.delete(ids=old_ids)
        
        # 6️⃣ Add new documents
        print(f"Adding {len(split_docs)} new embeddings for role: {role}")
        vector_store.add_documents(documents=split_docs, ids=new_ids)

        # 7️⃣ Save mapping
        role_doc_ids[role] = new_ids
        save_role_doc_ids(role_doc_ids)

        # 8️⃣ Save vector store
        print("Saving vector store...")
        vector_store.save_local(FAISS_PATH)

        response = f"✅ Embeddings updated for role: {role} ({len(split_docs)} chunks)"
        print(response)
        return response

    except Exception as e:
        error_msg = f"❌ Failed to load {filename}: {str(e)}"
        print(error_msg)
        raise ValueError(error_msg)  # Re-raise to handle upstream
    
    finally:
        # 9️⃣ Clean up temporary file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                print(f"Cleaned up temporary file: {temp_path}")
            except Exception as e:
                print(f"Warning: Could not delete temporary file: {e}")
