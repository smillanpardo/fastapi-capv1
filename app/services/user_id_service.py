"""
Servicio para generar IDs de usuario con formato op-XXX o ap-XXX
"""
from sqlalchemy.orm import Session
from models.user import Usuario
from models.transaction import UserRole
import re


class UserIdService:
    """
    Servicio para generar IDs consecutivos de usuarios basados en su rol.
    Formato: op-001, op-002... para OPERADOR
             ap-001, ap-002... para APROBADOR
    """
    
    DIGITS = 3  # Número de dígitos para el consecutivo
    
    def __init__(self, db: Session):
        self.db = db
    
    def generar_siguiente_user_id(self, role: UserRole) -> str:
        """
        Genera el siguiente user_id consecutivo basado en el rol.
        
        Args:
            role: Rol del usuario (OPERADOR o APROBADOR)
            
        Returns:
            str: Nuevo user_id con formato op-XXX o ap-XXX
        """
        # Determinar prefijo según el rol
        prefix = "op-" if role == UserRole.OPERADOR else "ap-"
        
        # Buscar el último user_id con este prefijo
        usuarios = self.db.query(Usuario).filter(
            Usuario.user_id.like(f"{prefix}%")
        ).all()
        
        if not usuarios:
            # Primer usuario con este rol
            return f"{prefix}{'0' * (self.DIGITS - 1)}1"
        
        # Extraer números de todos los user_ids con este prefijo
        numeros = []
        pattern = re.compile(rf"{prefix}(\d+)")
        
        for usuario in usuarios:
            if usuario.user_id:
                match = pattern.match(usuario.user_id)
                if match:
                    numeros.append(int(match.group(1)))
        
        if not numeros:
            return f"{prefix}{'0' * (self.DIGITS - 1)}1"
        
        # Obtener el siguiente número
        siguiente_numero = max(numeros) + 1
        
        # Formatear con ceros a la izquierda
        return f"{prefix}{str(siguiente_numero).zfill(self.DIGITS)}"
