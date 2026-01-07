from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.auth import LoginRequest
from app.db.crud import get_user_by_username
from app.core.security import verify_password
from app.dependencies.db import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    print(data)
    user = get_user_by_username(db, data.username)
    print(user)
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "username": user.username,
        "role": user.role.name
    }
