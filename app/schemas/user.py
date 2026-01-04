from pydantic import BaseModel, EmailStr
from models.transaction import UserRole

## Usuario
class UsuarioBase(BaseModel):
    nombre: str
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    password: str
    role: UserRole  # OPERADOR o APROBADOR

class UsuarioResponse(UsuarioBase):
    id: int
    user_id: str  # op-001, ap-001, etc.
    role: UserRole
    class Config:
        from_attributes = True    
