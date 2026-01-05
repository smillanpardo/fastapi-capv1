from sqlalchemy.orm import Session
from sqlalchemy import func
from models.transaction import Transaction
import re


class ReferenceService:
    PREFIX = "TRX"
    DIGITS = 3  # Número de dígitos (001, 002, etc.)
    
    @staticmethod
    def generar_siguiente_reference(db: Session) -> str:
        # Obtener la última transacción
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
        ultima_transaccion = (
            db.query(Transaction)
            .filter(Transaction.reference.like(f"{ReferenceService.PREFIX}-%"))
            .order_by(Transaction.created_at.desc())
            .first()
        )
        
        return ultima_transaccion.reference if ultima_transaccion else None
    
    @staticmethod
    def validar_reference_format(reference: str) -> bool:
        pattern = f"^{ReferenceService.PREFIX}-\\d{{{ReferenceService.DIGITS}}}$"
        return bool(re.match(pattern, reference))
