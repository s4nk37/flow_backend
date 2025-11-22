import uuid
from sqlalchemy.orm import Session
from app.models.user_model import UserModel
from app.core.security import hash_password

def create_user(db: Session, email: str, password: str, name: str | None = None):
    user = UserModel(id=str(uuid.uuid4()), email=email, hashed_password=hash_password(password), name=name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str):
    return db.query(UserModel).filter(UserModel.email == email).first()