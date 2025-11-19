from sqlalchemy import Column, Integer, String
from app.database.session import Base
from sqlalchemy.orm import relationship

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # phone=Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    todos = relationship("TodoModel", back_populates="user")  # user -> todos
