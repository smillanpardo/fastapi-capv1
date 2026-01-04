"""
Dependencias de autenticación para API v2 con JWT real.
Valida token y obtiene usuario + rol desde la base de datos.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from core.security import verificar_token
from core.config import setting
from deps.deps import get_db
from crud.user import obtener_usuario_por_email
from models.transaction import UserRole

oauth2_scheme_v2 = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user_v2(
    token: str = Depends(oauth2_scheme_v2),
    db: Session = Depends(get_db)
):
    """
    Obtiene el usuario actual desde el token JWT.
    Valida contra la base de datos.
    
    Returns:
        Usuario: Objeto usuario de la BD
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = verificar_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Obtener usuario de la BD
    user = obtener_usuario_por_email(db, email)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_role_v2(
    current_user = Depends(get_current_user_v2)
) -> str:
    """
    Obtiene el rol del usuario actual desde la BD.
    
    Returns:
        str: Rol del usuario (OPERADOR o APROBADOR)
    
    Raises:
        HTTPException: Si el usuario no tiene rol asignado
    """
    if not current_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario no tiene rol asignado. Contacte al administrador."
        )
    
    return current_user.role.value


async def require_operador_v2(
    current_user = Depends(get_current_user_v2)
):
    """
    Valida que el usuario tenga rol OPERADOR.
    
    Returns:
        Usuario: Usuario validado
    
    Raises:
        HTTPException: Si el usuario no es OPERADOR
    """
    if not current_user.role or current_user.role != UserRole.OPERADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol OPERADOR para esta acción"
        )
    return current_user


async def require_aprobador_v2(
    current_user = Depends(get_current_user_v2)
):
    """
    Valida que el usuario tenga rol APROBADOR.
    
    Returns:
        Usuario: Usuario validado
    
    Raises:
        HTTPException: Si el usuario no es APROBADOR
    """
    if not current_user.role or current_user.role != UserRole.APROBADOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol APROBADOR para esta acción"
        )
    return current_user
