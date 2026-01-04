from sqlalchemy import Column, Integer, String, Enum as SQLAlchemyEnum
from db.database import Base
from models.transaction import UserRole

class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True, nullable=False)  # op-001, ap-001, etc.
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(SQLAlchemyEnum(UserRole), nullable=False)  # OPERADOR o APROBADOR

