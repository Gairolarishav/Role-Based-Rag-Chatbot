# Role-Based RAG Chatbot 🤖

A secure, role-based AI chatbot system that provides intelligent document question-answering capabilities with role-specific access control. Built with FastAPI, LangChain, and Streamlit.

## 🌟 Features

- **Role-Based Access Control (RBAC)**: Users can only access documents and chat with content specific to their assigned role
- **RAG System**: Retrieval-Augmented Generation using FAISS vector store for accurate, context-aware responses
- **User Authentication**: Secure login system with credential management
- **Admin Dashboard**: Complete administrative control for managing users, roles, and documents
- **Document Management**: Upload and manage PDF documents for each role
- **Real-time Chat Interface**: Interactive chatbot powered by Google Gemini
- **Vector Store Management**: Automatic creation and updating of role-specific vector stores

## 🏗️ Architecture
```
┌─────────────┐
│  Streamlit  │  (Frontend - User Interface)
│   Frontend  │
└──────┬──────┘
       │
       │ HTTP/REST
       │
┌──────▼──────┐
│   FastAPI   │  (Backend - API Server)
│   Backend   │
└──────┬──────┘
       │
       ├─────────────┬─────────────┬──────────────┐
       │             │             │              │
┌──────▼──────┐ ┌───▼────┐  ┌────▼─────┐  ┌─────▼──────┐
│  LangChain  │ │ FAISS  │  │  Gemini  │  │    User    │
│     RAG     │ │Vector  │  │Embedding │  │    Auth    │
│   System    │ │ Store  │  │   & LLM  │  │  Database  │
└─────────────┘ └────────┘  └──────────┘  └────────────┘
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance API framework
- **LangChain**: LLM orchestration and RAG pipeline
- **FAISS**: Vector similarity search
- **Google Gemini**: Embedding generation and LLM
- **Python 3.13**

### Frontend
- **Streamlit**: Interactive web interface

### Data Storage
- **FAISS Vector Store**: Role-specific document embeddings
- **Local File System**: PDF document storage

## 📋 Prerequisites

- Python 3.13 or higher
- Google Gemini API key

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/Gairolarishav/Role-Based-Rag-Chatbot.git
cd role-based-rag-chatbot
```

2. **Create virtual environment**
```bash
pip install uv
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
uv sync
```

4. **Set up environment variables**
```bash
# Create .env file
touch .env

# Add your API keys
echo "GEMINI_API_KEY=your_gemini_api_key_here" >> .env
```

## ⚙️ Configuration

Create a `.env` file in the root directory:
```env
# API Keys
GEMINI_API_KEY=your_gemini_api_key
```

## 🏃 Running the Application

### Start Backend Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
streamlit run frontend.py
```

Access the application at:
- Frontend: `http://localhost:8501`
- Backend API: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - User login

### Role Management
- `GET /roles` - List all roles
- `POST /roles` - Create new role (Admin only)

### User Management
- `GET /users` - List all users (Admin only)
- `POST /users` - Create new user (Admin only)
  
### Chat
- `POST /chat` - Send message and get AI response

## 👥 User Roles

### Admin
- Create/manage users and roles
- Upload and manage documents
- Full system access

### Regular User
- Chat with documents specific to their role
- View their role information
- Limited to role-specific content

## 🔒 Security Features
- Role-based access control
- Secure password hashing

## 📝 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
