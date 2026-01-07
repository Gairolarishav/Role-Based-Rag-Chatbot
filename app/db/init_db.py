from .database import engine, SessionLocal
from .models import Base, Role

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    default_roles = [
        "engineering",
        "marketing",
        "finance",
        "hr",
        "employee",
        "c-levelexecutives"
    ]

    for role in default_roles:
        exists = db.query(Role).filter(Role.name == role).first()
        if not exists:
            db.add(Role(name=role, description=f"{role} role"))

    db.commit()
    db.close()
