from pydantic import BaseModel, Field, validator
from decimal import Decimal
from datetime import datetime
from typing import Optional
from models.transaction import TransactionStatus, UserRole


# ========== Request Schemas ==========

class TransactionCreate(BaseModel):
    """Schema para crear una nueva transacción (v1 - con reference manual)"""
    reference: str = Field(..., min_length=1, max_length=100, description="Referencia de la transacción")
    amount: Decimal = Field(..., gt=0, description="Monto de la transacción (debe ser mayor a 0)")
    currency: str = Field(..., min_length=3, max_length=3, description="Código de moneda (3 caracteres)")
    
    @validator('currency')
    def currency_must_be_uppercase(cls, v):
        """Valida que la moneda esté en mayúsculas"""
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "reference": "TRX-001",
                "amount": 5000.00,
                "currency": "MXN"
            }
        }


class TransactionCreateV2(BaseModel):
    """Schema para crear una nueva transacción (v2 - reference autogenerado)"""
    amount: Decimal = Field(..., gt=0, description="Monto de la transacción (debe ser mayor a 0)")
    currency: str = Field(..., min_length=3, max_length=3, description="Código de moneda (3 caracteres)")
    
    @validator('currency')
    def currency_must_be_uppercase(cls, v):
        """Valida que la moneda esté en mayúsculas"""
        return v.upper()
    
    class Config:
        json_schema_extra = {
            "example": {
                "amount": 5000.00,
                "currency": "MXN"
            }
        }

# ========== Response Schemas ==========

class TransactionResponse(BaseModel):
    """Schema de respuesta completa de una transacción"""
    transaction_id: str
    reference: str
    amount: Decimal
    currency: str
    status: TransactionStatus
    created_by: str
    approved_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Anteriormente orm_mode = True
        json_schema_extra = {
            "example": {
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "reference": "TRX-001",
                "amount": 5000.00,
                "currency": "MXN",
                "status": "APPROVED",
                "created_by": "op-123",
                "approved_by": "ap-456",
                "created_at": "2026-01-02T10:30:00",
                "updated_at": "2026-01-02T11:00:00"
            }
        }


class TransactionStatusUpdate(BaseModel):
    """Schema para actualización de estado"""
    status: TransactionStatus
    updated_by: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "APPROVED",
                "updated_by": "ap-456"
            }
        }


# ========== Message Response ==========

class MessageResponse(BaseModel):
    """Schema genérico para mensajes de respuesta"""
    message: str
    transaction_id: str
    status: TransactionStatus
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Transacción aprobada exitosamente",
                "transaction_id": "123e4567-e89b-12d3-a456-426614174000",
                "status": "APPROVED"
            }
        }
