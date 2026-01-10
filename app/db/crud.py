from sqlalchemy.orm import Session
from .models import User, Role
from core.security import hash_password

# ROLES
def create_role(db: Session, name: str, description: str):
    role = Role(name=name, description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

def get_roles(db: Session):
    return db.query(Role).all()

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()


# USERS
def create_user(db: Session, username: str, password: str, role: Role):
    user = User(
        username=username,
        password_hash=hash_password(password),
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session):
    return db.query(User).all()

