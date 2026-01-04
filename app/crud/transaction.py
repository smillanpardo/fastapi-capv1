from sqlalchemy.orm import Session
from models.transaction import Transaction, TransactionStatus
from schemas.transaction import TransactionCreate
from typing import Optional, List
import uuid


def crear_transaccion(db: Session, transaccion: TransactionCreate, created_by: str) -> Transaction:
    """
    Crea una nueva transacción en estado DRAFT.
    
    Args:
        db: Sesión de base de datos
        transaccion: Datos de la transacción
        created_by: ID del operador que crea la transacción
    
    Returns:
        Transaction: Transacción creada
    """
    db_transaction = Transaction(
        transaction_id=str(uuid.uuid4()),
        reference=transaccion.reference,
        amount=transaccion.amount,
        currency=transaccion.currency.upper(),
        status=TransactionStatus.DRAFT,
        created_by=created_by
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def obtener_transaccion_por_id(db: Session, transaction_id: str) -> Optional[Transaction]:
    """
    Obtiene una transacción por su ID.
    
    Args:
        db: Sesión de base de datos
        transaction_id: UUID de la transacción
    
    Returns:
        Optional[Transaction]: Transacción encontrada o None
    """
    return db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()


def obtener_todas_transacciones(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TransactionStatus] = None
) -> List[Transaction]:
    """
    Obtiene todas las transacciones con paginación opcional.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a saltar
        limit: Número máximo de registros a retornar
        status: Filtrar por estado específico
    
    Returns:
        List[Transaction]: Lista de transacciones
    """
    query = db.query(Transaction)
    
    if status:
        query = query.filter(Transaction.status == status)
    
    return query.offset(skip).limit(limit).all()


def actualizar_estado_transaccion(
    db: Session,
    transaction_id: str,
    nuevo_estado: TransactionStatus,
    approved_by: Optional[str] = None
) -> Optional[Transaction]:
    """
    Actualiza el estado de una transacción.
    
    Args:
        db: Sesión de base de datos
        transaction_id: UUID de la transacción
        nuevo_estado: Nuevo estado de la transacción
        approved_by: ID del aprobador (opcional)
    
    Returns:
        Optional[Transaction]: Transacción actualizada o None
    """
    db_transaction = obtener_transaccion_por_id(db, transaction_id)
    
    if not db_transaction:
        return None
    
    db_transaction.status = nuevo_estado
    
    if approved_by:
        db_transaction.approved_by = approved_by
    
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def eliminar_transaccion(db: Session, transaction_id: str) -> bool:
    """
    Elimina una transacción (solo para testing/admin).
    
    Args:
        db: Sesión de base de datos
        transaction_id: UUID de la transacción
    
    Returns:
        bool: True si se eliminó, False si no existe
    """
    db_transaction = obtener_transaccion_por_id(db, transaction_id)
    
    if not db_transaction:
        return False
    
    db.delete(db_transaction)
    db.commit()
    return True
