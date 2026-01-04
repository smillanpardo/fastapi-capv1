from sqlalchemy.orm import Session 
from models.user import  Usuario
from schemas.user import *
from core.security import hash_password
from sqlalchemy import or_
from services.user_id_service import UserIdService





### Usuarios CRUD

def obtener_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email).first()

def obtener_usuario_por_id(db: Session, usuario_id: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.user_id == usuario_id).first()

def crear_usuario(db:Session, usuario: UsuarioCreate) -> Usuario:
    existe = db.query(Usuario).filter(
        or_(Usuario.email == usuario.email, Usuario.nombre == usuario.nombre)
    ).first()
    if existe:
        raise ValueError("Ya existe un usuario con este Email o Nombre")
    
    # Generar user_id automático basado en el rol
    user_id_service = UserIdService(db)
    nuevo_user_id = user_id_service.generar_siguiente_user_id(usuario.role)
    
    db_usuario = Usuario(
        user_id=nuevo_user_id,
        nombre = usuario.nombre,
        email = usuario.email,
        hashed_password = hash_password(usuario.password),
        role = usuario.role
    )   
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario