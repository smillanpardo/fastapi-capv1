from schemas.user import UsuarioBase, EmailStr, BaseModel, UsuarioCreate, UsuarioResponse
from schemas.token import BaseModel, Token
from crud.user import crear_usuario, obtener_usuario_por_email
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from core.security import verify_password, crear_token
from deps.deps import get_current_user, get_db

api_router = APIRouter(tags=["Authentication"])

@api_router.post("/usuarios", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
def registrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    try:
        return crear_usuario(db, usuario)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@api_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = obtener_usuario_por_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    
    # Validar que el usuario tenga rol asignado
    if not user.role:
        raise HTTPException(status_code=403, detail="Usuario sin rol asignado. Contacte al administrador.")
    
    token = crear_token(sub=user.email, role=user.role.value)
    return {"access_token": token, "token_type": "bearer"}

@api_router.get("/usuarios/me", response_model=UsuarioResponse)
def leer_perfil(current_user = Depends(get_current_user)):
    return current_user