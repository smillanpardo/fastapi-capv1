from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from models.transaction import Transaction, TransactionStatus, UserRole
from schemas.transaction import TransactionCreate
import crud.transaction as crud_transaction
from typing import Optional


class TransactionService:
    """
    Servicio que implementa la lógica de negocio y la máquina de estados
    para el flujo Operador-Aprobador de transacciones.
    """
    
    # Matriz de transiciones válidas de estados
    VALID_TRANSITIONS = {
        TransactionStatus.DRAFT: [TransactionStatus.PENDING_APPROVAL],
        TransactionStatus.PENDING_APPROVAL: [TransactionStatus.APPROVED, TransactionStatus.REJECTED],
        TransactionStatus.APPROVED: [TransactionStatus.EXECUTED],
        TransactionStatus.REJECTED: [],  # Estado final
        TransactionStatus.EXECUTED: []   # Estado final
    }
    
    @staticmethod
    def crear_transaccion(
        db: Session,
        transaccion: TransactionCreate,
        user_id: str,
        user_role: str
    ) -> Transaction:
        """
        Regla 1: Solo un OPERADOR puede crear transacciones.
        La transacción se crea en estado DRAFT.
        """
        if user_role != UserRole.OPERADOR.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con rol OPERADOR pueden crear transacciones"
            )
        
        # Validaciones de negocio
        if transaccion.amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El monto debe ser mayor a cero"
            )
        
        if len(transaccion.currency) != 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La moneda debe tener exactamente 3 caracteres"
            )
        
        # Intentar crear la transacción
        try:
            return crud_transaction.crear_transaccion(db, transaccion, user_id)
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una transacción con la referencia '{transaccion.reference}'"
            )
    
    @staticmethod
    def enviar_a_aprobacion(
        db: Session,
        transaction_id: str,
        user_role: str
    ) -> Transaction:
        """
        Regla 2: Solo el OPERADOR puede enviar la transacción a aprobación.
        El estado cambia de DRAFT a PENDING_APPROVAL.
        """
        if user_role != UserRole.OPERADOR.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con rol OPERADOR pueden enviar a aprobación"
            )
        
        transaction = crud_transaction.obtener_transaccion_por_id(db, transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        # Validar transición de estado
        if transaction.status != TransactionStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Solo se pueden enviar a aprobación transacciones en estado DRAFT. Estado actual: {transaction.status}"
            )
        
        return crud_transaction.actualizar_estado_transaccion(
            db, transaction_id, TransactionStatus.PENDING_APPROVAL
        )
    
    @staticmethod
    def aprobar_transaccion(
        db: Session,
        transaction_id: str,
        user_id: str,
        user_role: str
    ) -> Transaction:
        """
        Regla 3: Solo un APROBADOR puede aprobar.
        Solo se pueden aprobar transacciones en estado PENDING_APPROVAL.
        """
        if user_role != UserRole.APROBADOR.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con rol APROBADOR pueden aprobar transacciones"
            )
        
        transaction = crud_transaction.obtener_transaccion_por_id(db, transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        # Validar transición de estado
        if transaction.status != TransactionStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Solo se pueden aprobar transacciones en estado PENDING_APPROVAL. Estado actual: {transaction.status}"
            )
        
        return crud_transaction.actualizar_estado_transaccion(
            db, transaction_id, TransactionStatus.APPROVED, approved_by=user_id
        )
    
    @staticmethod
    def rechazar_transaccion(
        db: Session,
        transaction_id: str,
        user_role: str
    ) -> Transaction:
        """
        Regla 4: Solo un APROBADOR puede rechazar.
        El estado pasa a REJECTED.
        """
        if user_role != UserRole.APROBADOR.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Solo usuarios con rol APROBADOR pueden rechazar transacciones"
            )
        
        transaction = crud_transaction.obtener_transaccion_por_id(db, transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        # Validar que esté en estado válido para rechazo
        if transaction.status != TransactionStatus.PENDING_APPROVAL:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Solo se pueden rechazar transacciones en estado PENDING_APPROVAL. Estado actual: {transaction.status}"
            )
        
        return crud_transaction.actualizar_estado_transaccion(
            db, transaction_id, TransactionStatus.REJECTED
        )
    
    @staticmethod
    def ejecutar_transaccion(
        db: Session,
        transaction_id: str
    ) -> Transaction:
        """
        Regla 5: Solo transacciones en estado APPROVED pueden ejecutarse.
        La ejecución es simulada (sin integración externa).
        """
        transaction = crud_transaction.obtener_transaccion_por_id(db, transaction_id)
        
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transacción no encontrada"
            )
        
        # Validar que esté aprobada
        if transaction.status != TransactionStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Solo se pueden ejecutar transacciones en estado APPROVED. Estado actual: {transaction.status}"
            )
        
        # Simulación de ejecución (sin integración real)
        # Aquí iría la lógica de integración con sistemas externos
        
        return crud_transaction.actualizar_estado_transaccion(
            db, transaction_id, TransactionStatus.EXECUTED
        )
    
    @staticmethod
    def validar_transicion(estado_actual: TransactionStatus, estado_nuevo: TransactionStatus) -> bool:
        """
        Valida si una transición de estado es válida según la máquina de estados.
        """
        transiciones_validas = TransactionService.VALID_TRANSITIONS.get(estado_actual, [])
        return estado_nuevo in transiciones_validas
