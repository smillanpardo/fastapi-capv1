from fastapi import Header, HTTPException, status
from typing import Optional
from models.transaction import UserRole


async def get_user_role(
    x_user_role: Optional[str] = Header(None, description="Rol del usuario: OPERADOR o APROBADOR")
) -> str:
    """
    Extrae y valida el rol del usuario desde el header X-User-Role.
    
    Args:
        x_user_role: Header con el rol del usuario
    
    Returns:
        str: Rol del usuario validado
    
    Raises:
        HTTPException: Si el header no está presente o el rol es inválido
    """
    if not x_user_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header X-User-Role es requerido"
        )
    
    # Validar que el rol sea válido
    try:
        role = UserRole(x_user_role.upper())
        return role.value
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Rol inválido. Valores permitidos: {', '.join([r.value for r in UserRole])}"
        )


async def get_user_id(
    x_user_id: Optional[str] = Header(None, description="ID del usuario")
) -> str:
    """
    Extrae el ID del usuario desde el header X-User-Id.
    
    Args:
        x_user_id: Header con el ID del usuario
    
    Returns:
        str: ID del usuario
    
    Raises:
        HTTPException: Si el header no está presente
    """
    if not x_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Header X-User-Id es requerido"
        )
    
    return x_user_id


async def require_operador(role: str = Header(..., alias="X-User-Role")) -> str:
    """
    Valida que el usuario tenga rol OPERADOR.
    
    Args:
        role: Rol del usuario desde header
    
    Returns:
        str: Rol validado
    
    Raises:
        HTTPException: Si el usuario no es OPERADOR
    """
    if role.upper() != UserRole.OPERADOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol OPERADOR para esta acción"
        )
    return role.upper()


async def require_aprobador(role: str = Header(..., alias="X-User-Role")) -> str:
    """
    Valida que el usuario tenga rol APROBADOR.
    
    Args:
        role: Rol del usuario desde header
    
    Returns:
        str: Rol validado
    
    Raises:
        HTTPException: Si el usuario no es APROBADOR
    """
    if role.upper() != UserRole.APROBADOR.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol APROBADOR para esta acción"
        )
    return role.upper()
