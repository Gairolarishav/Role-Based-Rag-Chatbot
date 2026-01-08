import requests
import json
from pathlib import Path
from datetime import datetime, timedelta
import os
from dotend import load_env

load_env()

API_BASE_URL = os.getenv("API_BASE_URL")


# Directory for storing temporary session files
TEMP_SESSION_DIR = Path("temp_sessions")
TEMP_SESSION_DIR.mkdir(exist_ok=True)

# Session timeout (in minutes) - sessions older than this will be auto-deleted
SESSION_TIMEOUT_MINUTES = 30

def generate_session_id():
    """Generate a unique session ID"""
    import uuid
    return str(uuid.uuid4())

def get_session_file(session_id):
    """Get the file path for a session"""
    return TEMP_SESSION_DIR / f"session_{session_id}.json"

def cleanup_old_sessions():
    """Remove session files older than timeout"""
    try:
        cutoff_time = datetime.now() - timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        for file in TEMP_SESSION_DIR.glob("session_*.json"):
            if datetime.fromtimestamp(file.stat().st_mtime) < cutoff_time:
                file.unlink()
    except Exception as e:
        print(f"Error cleaning up sessions: {e}")

def save_session(session_id, data):
    """Save session data to file"""
    file_path = get_session_file(session_id)
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving session: {e}")

def load_session(session_id):
    """Load session data from file"""
    file_path = get_session_file(session_id)
    if file_path.exists():
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading session: {e}")
    return None

def delete_session(session_id):
    """Delete session file"""
    file_path = get_session_file(session_id)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            print(f"Error deleting session: {e}")

def get_roles():
    """Get all roles"""
    try:
        url = "https://role-based-rag-chatbot.onrender.com/roles/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return str(e)


def chat_api_call_stream(message, user_role):
    """Call the streaming chat API endpoint"""
    try:
        payload = {
            "user_query": message,
            "user_role": user_role
        }
        
        response = requests.post(
            "https://role-based-rag-chatbot.onrender.com/chat/",
            json=payload,
            stream=False,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            return (
                True,
                data.get("answer", ""),
                data.get("tool_name"),
                data.get("sources")
            )
        elif response.status_code == 403:
            return False, "Role mismatch.", None, None
        else:
            return False, f"Chat failed ({response.status_code})", None, None
            
    except Exception as e:
        return False, str(e), None, None
    

def create_user(username, password, role):
    """Create a new user"""
    try:
        payload = {
            "username": username,
            "password": password,
            "role_name": role
        }
        
        response = requests.post(
            "https://role-based-rag-chatbot.onrender.com/users/",
            json=payload,
            timeout=30
        )

        data = response.json()
        
        if response.status_code == 201:
            return True, data['id']
        elif response.status_code == 409:
            return False, "User already exists."

        else:
            return False, f"User creation failed ({response.status_code})"
            
    except Exception as e:
        return False, str(e)

def create_role(name, description):
    """Create a new user"""
    try:
        payload = {
            "name": name,
            "description": description
        }
        
        response = requests.post(
            "https://role-based-rag-chatbot.onrender.com/roles/",
            json=payload,
            timeout=30
        )

        data = response.json()
        print(data['id'])
        
        if response.status_code == 201:
            return True, data['id']
        elif response.status_code == 409:
            return False, "Role already exists."

        else:
            return False, f"Role creation failed ({response.status_code})"
            
    except Exception as e:
        return False, str(e)
