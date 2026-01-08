import streamlit as st
import requests
import time
from helper import (
    create_role, create_user, cleanup_old_sessions, load_session, 
    save_session, delete_session, generate_session_id, 
    chat_api_call_stream, get_roles
)
import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")

# Page configuration
st.set_page_config(
    page_title="Role-Based AI Chatbot",
    page_icon="🔐",
    layout="wide"
)

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .stTextInput > div > div > input {
        background-color: #f7fafc;
        border: 2px solid #e2e8f0;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    div[data-testid="stForm"] {
        background-color: white;
        padding: 40px;
        border-radius: 20px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }
    
    .login-header {
        text-align: center;
        color: #2d3748;
        margin-bottom: 30px;
    }
    
    .login-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .login-subtitle {
        font-size: 16px;
        color: #718096;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px;
        font-size: 16px;
        font-weight: 600;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    .user-info {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    
    .chat-container {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Clean up old sessions on startup
cleanup_old_sessions()

# Initialize session state with persistence
def initialize_session_state():
    """Initialize all session state variables"""
    if 'session_id' not in st.session_state:
        query_params = st.query_params
        if 'sid' in query_params:
            st.session_state.session_id = query_params['sid']
            session_data = load_session(st.session_state.session_id)
            if session_data:
                st.session_state.logged_in = session_data.get('logged_in', False)
                st.session_state.username = session_data.get('username')
                st.session_state.role = session_data.get('role')
                st.session_state.chat_history = session_data.get('chat_history', [])
            else:
                st.session_state.logged_in = False
                st.session_state.username = None
                st.session_state.role = None
                st.session_state.chat_history = []
        else:
            st.session_state.session_id = generate_session_id()
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.role = None
            st.session_state.chat_history = []
    
    if 'menu_option' not in st.session_state:
        st.session_state.menu_option = "💬 Chatbot"
    
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False
    
    if 'creating_user' not in st.session_state:
        st.session_state.creating_user = False
    
    if 'creating_role' not in st.session_state:
        st.session_state.creating_role = False

initialize_session_state()

def persist_session():
    """Save current session state to file and update URL"""
    if st.session_state.logged_in:
        session_data = {
            'logged_in': st.session_state.logged_in,
            'username': st.session_state.username,
            'role': st.session_state.role,
            'chat_history': st.session_state.chat_history
        }
        save_session(st.session_state.session_id, session_data)
        st.query_params['sid'] = st.session_state.session_id

def login(username, password):
    """Login function that hits the FastAPI authentication endpoint"""
    try:

        st.write(f"{API_BASE_URL}/auth/login")

        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=30
        )
        st.write("response :", response.json())
        
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.username = data['username']
            st.session_state.role = data['role']
            st.session_state.chat_history = []
            persist_session()
            return True, data
        elif response.status_code == 401:
            return False, "Invalid credentials"
        else:
            return False, f"Login failed with status code: {response.status_code}"
            
    except requests.exceptions.ConnectionError:
        return False, "Could not connect to the server. Please ensure the API is running."
    except requests.exceptions.Timeout:
        return False, "Request timed out. Please try again."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

def clear_chat_callback():
    """Callback for clear chat button"""
    if not st.session_state.is_processing:
        st.session_state.chat_history = []
        persist_session()

def logout_callback():
    """Callback for logout button"""
    if not st.session_state.is_processing:
        delete_session(st.session_state.session_id)
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.chat_history = []
        st.query_params.clear()
        st.session_state.session_id = generate_session_id()

def render_login_page():
    """Render the login page"""
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        st.markdown("""
            <div class="login-header">
                <div class="login-title">🔐 Role Based AI Chatbot</div>
                <div class="login-subtitle">Please login to your account</div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter your username", key="username_input")
            password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")
            
            st.write("")
            submit = st.form_submit_button("Login")
            
            if submit:
                if username and password:
                    with st.spinner("Authenticating..."):
                        success, result = login(username, password)
                    
                    if success:
                        st.success("Login successful! 🎉")
                        st.rerun()
                    else:
                        st.error(result)
                else:
                    st.error("Please enter both username and password")

def render_sidebar():
    """Render the sidebar with user info and menu"""
    with st.sidebar:
        st.markdown("""
            <div class="user-info">
                <h3 style="margin: 0; color: #2d3748;">👤 User Info</h3>
                <hr style="margin: 10px 0;">
                <p style="margin: 5px 0;"><strong>Username:</strong> {}</p>
                <p style="margin: 5px 0;"><strong>Role:</strong> {}</p>
            </div>
        """.format(st.session_state.username, st.session_state.role), unsafe_allow_html=True)
        
        st.markdown("### 📋 Menu")
        menu_option = st.radio(
            "Select Option",
            ["💬 Chatbot", "📁 Upload Documents", "👥 User Management"],
            label_visibility="collapsed",
            disabled=st.session_state.is_processing,
            key="menu_radio"
        )
        
        # Trigger rerun if menu changed
        if menu_option != st.session_state.menu_option:
            st.session_state.menu_option = menu_option
            st.rerun()
        
        st.markdown("---")
        
        # Clear Chat button with callback
        clear_btn = st.button(
            "🗑️ Clear Chat", 
            use_container_width=True,
            disabled=st.session_state.is_processing,
            on_click=clear_chat_callback,
            key="clear_chat_btn"
        )
        if clear_btn:
            st.success("Chat history cleared!")
            time.sleep(1)
            st.rerun()
        
        # Logout button with callback
        logout_btn = st.button(
            "🚪 Logout", 
            use_container_width=True,
            disabled=st.session_state.is_processing,
            on_click=logout_callback,
            key="logout_btn"
        )
        if logout_btn:
            st.rerun()

def render_chatbot():
    """Render the chatbot interface"""
    st.markdown(
        "<h1 style='text-align: center;'>💬 Role Based AI Chatbot</h1>",
        unsafe_allow_html=True
    )
    
    # Create a container for chat messages
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...", disabled=st.session_state.is_processing, key="chat_input_main")
    
    if user_input and not st.session_state.is_processing:
        st.session_state.is_processing = True
        
        # Add user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            spinner_placeholder = st.empty()

            spinner_placeholder.markdown("⏳ *Thinking...*")

            success, answer, tool_name, sources = chat_api_call_stream(
                user_input,
                st.session_state.role
            )

            spinner_placeholder.empty()

            if success:
                final_markdown = ""

                # Tool info
                if tool_name:
                    final_markdown += f"**🛠 Tool used:** `{tool_name}`\n\n"

                # Main answer
                final_markdown += answer

                # Sources at bottom
                if sources:
                    seen = set()
                    unique_sources = []

                    for src in sources:
                        name = src.get("source")
                        if name and name not in seen:
                            seen.add(name)
                            unique_sources.append(name)

                    final_markdown += "\n\n---\n**Sources:**\n"
                    for name in unique_sources:
                        final_markdown += f"- 📄 `{name}`\n"

                message_placeholder.markdown(final_markdown)

                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": final_markdown
                })
            else:
                error_msg = f"❌ Error: {answer}"
                message_placeholder.markdown(error_msg)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": error_msg
                })
        
        # Reset processing state and persist session
        st.session_state.is_processing = False
        persist_session()
        st.rerun()

def render_document_upload():
    """Render the document upload interface"""
    if st.session_state.role != "c-levelexecutives":
        st.warning("You do not have access to this section.")
        return
    
    st.title("📁 Document Upload")

    roles = [role["name"] for role in get_roles()]
    
    # 🔑 Initialize uploader key
    if "upload_key" not in st.session_state:
        st.session_state.upload_key = 0

    st.subheader("Upload Document")

    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=["pdf"],
        key=f"file_uploader_{st.session_state.upload_key}",
        help="Upload documents related to your role"
    )

    document_role = st.selectbox(
        "Assign document to role",
        roles
    )

    if st.button("Upload to Knowledge Base"):
        if uploaded_file is None:
            st.warning("Please upload a PDF file")
        else:
            with st.spinner("Uploading and processing PDF..."):
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        "application/pdf"
                    )
                }

                params = {
                    "role": document_role
                }

                response = requests.post(
                    f"{API_BASE_URL}/embeddings/ingest/",
                    files=files,
                    params=params,
                    timeout=120
                )

                if response.status_code == 200:
                    st.success("✅ PDF ingested successfully")
                    st.json(response.json())

                     # 🔥 Reset uploader & UI
                    st.session_state.upload_key += 1

                    # Optional small delay for UX
                    time.sleep(1)

                    st.rerun()
                else:
                    st.error("❌ Upload failed")
                    st.text(response.text)

def render_user_management():
    """Render the user management interface"""
    if st.session_state.role != "c-levelexecutives":
        st.warning("You do not have access to this section.")
        return
    
    st.title("👥 User Management")
    
    tab1, tab2 = st.tabs(["Create User", "Create Role"])
    
    with tab1:
        st.subheader("Create New User")
        
        roles = [role["name"] for role in get_roles()]
    
        with st.form("create_user_form", clear_on_submit=True):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            user_role = st.selectbox("Assign Role", roles)
            
            submitted = st.form_submit_button(
                "Create User",
                disabled=st.session_state.creating_user or st.session_state.is_processing
            )
        
        if submitted:
            if not new_username or not new_password:
                st.error("Username and password are required")
            elif new_password != confirm_password:
                st.error("Passwords do not match")
            else:
                st.session_state.creating_user = True
                
                with st.spinner("Creating user..."):
                    success, result = create_user(
                        new_username,
                        new_password,
                        user_role
                    )
                
                st.session_state.creating_user = False
                
                if success:
                    st.success(f"✅ User created successfully (ID: {result})")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(result)
    
    with tab2:
        st.subheader("Create New Role")
        
        with st.form("create_role_form", clear_on_submit=True):
            role_name = st.text_input("Role Name")
            role_description = st.text_area("Role Description")
            
            submitted_role = st.form_submit_button(
                "Create Role",
                disabled=st.session_state.creating_role or st.session_state.is_processing
            )
        
        if submitted_role:
            if not role_name.strip():
                st.error("Role name is required")
            else:
                st.session_state.creating_role = True
                
                with st.spinner("Creating role..."):
                    success, result = create_role(role_name, role_description)
                
                st.session_state.creating_role = False
                
                if success:
                    st.success(f"✅ Role created successfully (ID: {result})")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(result)

# Main application logic
if not st.session_state.logged_in:
    render_login_page()
else:
    render_sidebar()
    
    # Render content based on menu selection
    if st.session_state.menu_option == "💬 Chatbot":
        render_chatbot()
    elif st.session_state.menu_option == "📁 Upload Documents":
        render_document_upload()
    elif st.session_state.menu_option == "👥 User Management":
        render_user_management()
