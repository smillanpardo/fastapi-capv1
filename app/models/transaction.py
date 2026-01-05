from sqlalchemy import Column, String, Numeric, Enum as SQLAlchemyEnum, DateTime
from db.database import Base
from datetime import datetime
import enum
import uuid


class TransactionStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXECUTED = "EXECUTED"


class UserRole(str, enum.Enum):
    OPERADOR = "OPERADOR"
    APROBADOR = "APROBADOR"


class Transaction(Base):
    __tablename__ = "transactions"
    
    transaction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    reference = Column(String, nullable=False, unique=True, index=True) 
    amount = Column(Numeric(precision=18, scale=2), nullable=False)
    currency = Column(String(3), nullable=False)
    status = Column(
        SQLAlchemyEnum(TransactionStatus),
        nullable=False,
        default=TransactionStatus.DRAFT
    )
    created_by = Column(String, nullable=False)
    approved_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f"<Transaction {self.transaction_id} - {self.reference} - {self.status}>"
