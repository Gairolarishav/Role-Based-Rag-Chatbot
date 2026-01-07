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
from langchain_community.document_loaders import UnstructuredMarkdownLoader, CSVLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv  
from pathlib import Path

load_dotenv()

# -------------------------------
# Configuration
# -------------------------------
BASE_DIR = Path(
    r"E:\Gen AI Roadmap\Gen AI Projects\Rolebased_AI_Chatbot_fintech\ds-rpc-01\resources\data"
)

embedding_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

# -------------------------------
# Aggregate all split documents
# -------------------------------
all_split_docs = []

for department in os.listdir(BASE_DIR):
    dept_path = os.path.join(BASE_DIR, department)

    if os.path.isdir(dept_path):
        print(f"\n🔍 Processing department: {department}")
        all_docs = []

        for file in os.listdir(dept_path):
            print('file====',file)
            file_path = os.path.join(dept_path, file)

            try:
                if file.endswith(".md"):
                    try:
                        loader = UnstructuredMarkdownLoader(file_path, mode="elements",strategy="fast",)
                        docs = loader.load()
                    except:
                        loader = TextLoader(file_path)
                        docs = loader.load()
                elif file.endswith(".csv"):
                    loader = CSVLoader(file_path)
                    docs = loader.load()
                else:
                    continue

                all_docs.extend(docs)

            except Exception as e:
                print(f"❌ Failed to load {file}: {e}")

        if not all_docs:
            print(f"⚠️ No documents found for department: {department}")
            continue

        # Split into chunks and tag with metadata
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        split_docs = splitter.split_documents(all_docs)
        for doc in split_docs:
            doc.metadata = {    # e.g. "engineering"
                "category": "general" if department.lower() == "general" else department.lower(),
                "source": file,
            }

        all_split_docs.extend(split_docs)
        print(f"✅ Loaded & split {len(split_docs)} documents for {department}")

# -------------------------------
# Build or refresh FAISS DB
# -------------------------------
shutil.rmtree('faiss_index', ignore_errors=True)

# Create FAISS database from already split documents
db = FAISS.from_documents(
    documents=all_split_docs,  # Use the already split documents
    embedding=embedding_model
)

# Save the database
faiss_path = r"E:\Gen AI Roadmap\Gen AI Projects\Rolebased_AI_Chatbot_fintech\ds-rpc-01\faiss_index"
db.save_local(faiss_path)

# Create retriever
retriever = db.as_retriever(search_kwargs={"k": 5})

print("\n🔍 Testing retrieval:")
results = retriever.invoke("API Gateway")
print(f"Retrieved {len(results)} documents")
if results:
    print(f"Sample result: {results[0].page_content[:200]}...")

# -------------------------------
# Summary
# -------------------------------
print(f"\n🎉 Successfully stored {len(all_split_docs)} documents in FAISS.")