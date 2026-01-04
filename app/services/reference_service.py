"""
Servicio para generar referencias de transacciones de forma consecutiva.
Formato: TRX-0001, TRX-0002, TRX-0003, etc.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.transaction import Transaction
import re


class ReferenceService:
    """Servicio para generar referencias consecutivas de transacciones"""
    
    PREFIX = "TRX"
    DIGITS = 3  # Número de dígitos (001, 002, etc.)
    
    @staticmethod
    def generar_siguiente_reference(db: Session) -> str:
        """
        Genera la siguiente referencia consecutiva.
        
        Args:
            db: Sesión de base de datos
        
        Returns:
            str: Referencia en formato TRX-001, TRX-002, etc.
        
        Example:
            >>> generar_siguiente_reference(db)
            'TRX-001'  # Si es la primera
            'TRX-042'  # Si ya hay 41 transacciones
        """
        # Obtener la última transacción con reference que siga el patrón TRX-XXXX
        ultima_transaccion = (
            db.query(Transaction)
            .filter(Transaction.reference.like(f"{ReferenceService.PREFIX}-%"))
            .order_by(Transaction.created_at.desc())
            .first()
        )
        
        if not ultima_transaccion:
            # Primera transacción
            siguiente_numero = 1
        else:
            # Extraer el número de la última referencia
            ultimo_reference = ultima_transaccion.reference
            match = re.search(r'TRX-(\d+)', ultimo_reference)
            
            if match:
                ultimo_numero = int(match.group(1))
                siguiente_numero = ultimo_numero + 1
            else:
                # Si no coincide con el patrón, contar todas
                siguiente_numero = db.query(Transaction).count() + 1
        
        # Formatear con ceros a la izquierda
        reference = f"{ReferenceService.PREFIX}-{str(siguiente_numero).zfill(ReferenceService.DIGITS)}"
        
        return reference
    
    @staticmethod
    def obtener_ultima_reference(db: Session) -> str:
        """
        Obtiene la última referencia generada.
        
        Args:
            db: Sesión de base de datos
        
        Returns:
            str: Última referencia o None si no hay transacciones
        """
        ultima_transaccion = (
            db.query(Transaction)
            .filter(Transaction.reference.like(f"{ReferenceService.PREFIX}-%"))
            .order_by(Transaction.created_at.desc())
            .first()
        )
        
        return ultima_transaccion.reference if ultima_transaccion else None
    
    @staticmethod
    def validar_reference_format(reference: str) -> bool:
        """
        Valida que una referencia tenga el formato correcto.
        
        Args:
            reference: Referencia a validar
        
        Returns:
            bool: True si es válida, False si no
        
        Example:
            >>> validar_reference_format("TRX-001")
            True
            >>> validar_reference_format("INVALID")
            False
        """
        pattern = f"^{ReferenceService.PREFIX}-\\d{{{ReferenceService.DIGITS}}}$"
        return bool(re.match(pattern, reference))
