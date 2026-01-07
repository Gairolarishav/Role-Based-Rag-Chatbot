from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.crud import create_role, get_roles
from schemas.role import RoleCreate, RoleResponse
from dependencies.db import get_db
from fastapi import status

router = APIRouter(prefix="/roles", tags=["Roles"])

@router.post("/", response_model=RoleResponse,status_code=status.HTTP_201_CREATED)
def add_role(role: RoleCreate, db: Session = Depends(get_db)):
    return create_role(db, role.name, role.description)

@router.get("/", response_model=list[RoleResponse])
def list_roles(db: Session = Depends(get_db)):
    return get_roles(db)
