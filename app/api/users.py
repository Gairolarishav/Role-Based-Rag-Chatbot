from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.crud import create_user, get_users,get_role_by_name,get_user_by_username
from app.schemas.user import UserCreate, UserResponse
from app.dependencies.db import get_db
from fastapi import status

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse,status_code=status.HTTP_201_CREATED)
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    role = get_role_by_name(db, user.role_name)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    new_user = create_user(db, user.username, user.password, role)

    return {
        "id": new_user.id,
        "username": new_user.username,
        "role": new_user.role.name
    }

@router.get("/", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    users = get_users(db)
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            role=u.role.name
        )
        for u in users
    ]
