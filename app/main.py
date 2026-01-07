from fastapi import FastAPI
from .api import roles, users, auth,chat
from db.init_db import init_db

app = FastAPI(title="RBAC Chatbot Backend")

app.include_router(roles.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(chat.router)
