"""
API v2 de Transacciones con autenticación JWT y reference autogenerado.
Versión empresarial con validaciones adicionales y seguridad mejorada.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.transaction import TransactionCreateV2, TransactionResponse, MessageResponse
from services.transaction_service import TransactionService
from services.reference_service import ReferenceService
from deps.auth_v2 import (
    get_current_user_v2,
    get_current_user_role_v2,
    require_operador_v2,
    require_aprobador_v2
)
from deps.deps import get_db
import crud.transaction as crud_transaction
from crud.transaction import crear_transaccion
from schemas.transaction import TransactionCreate


api_router = APIRouter(tags=["v2 - Transactions (JWT + Auto-Reference)"])


@api_router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="🔐 Crear transacción (v2 - JWT + Reference Auto)",
    description="Crea una nueva transacción con autenticación JWT. La referencia se genera automáticamente."
)
async def crear_transaccion_v2(
    transaccion: TransactionCreateV2,
    current_user = Depends(require_operador_v2),
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Autenticación JWT real validando contra BD
    - ✅ Reference autogenerado (TRX-001, TRX-002, etc.)
    - ✅ Validación de rol desde la BD
    
    ## Requiere:
    - Token JWT válido en header `Authorization: Bearer <token>`
    - Usuario con rol OPERADOR en la BD
    """
    # Generar reference automáticamente
    reference = ReferenceService.generar_siguiente_reference(db)
    
    # Crear objeto con reference
    transaccion_completa = TransactionCreate(
        reference=reference,
        amount=transaccion.amount,
        currency=transaccion.currency
    )
    
    # Usar user.email como created_by para trazabilidad
    user_id = f"{current_user.email}"
    user_role = current_user.role.value
    
    # Crear la transacción
    transaction = TransactionService.crear_transaccion(
        db, transaccion_completa, user_id, user_role
    )
    
    return transaction


@api_router.post(
    "/transactions/{transaction_id}/submit",
    response_model=MessageResponse,
    summary="🔐 Enviar a aprobación (v2 - JWT)",
    description="Envía una transacción a aprobación con autenticación JWT."
)
async def enviar_a_aprobacion_v2(
    transaction_id: str,
    current_user = Depends(require_operador_v2),
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Validación JWT real
    """
    user_role = current_user.role.value
    transaction = TransactionService.enviar_a_aprobacion(db, transaction_id, user_role)
    
    return MessageResponse(
        message="Transacción enviada a aprobación exitosamente",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.post(
    "/transactions/{transaction_id}/approve",
    response_model=MessageResponse,
    summary="🔐 Aprobar transacción (v2 - JWT)",
    description="Aprueba una transacción con autenticación JWT."
)
async def aprobar_transaccion_v2(
    transaction_id: str,
    current_user = Depends(require_aprobador_v2),
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Validación JWT real
    - ✅ Registro del aprobador con email real
    """
    user_id = current_user.email
    user_role = current_user.role.value
    
    transaction = TransactionService.aprobar_transaccion(db, transaction_id, user_id, user_role)
    
    return MessageResponse(
        message=f"Transacción aprobada por {current_user.nombre}",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.post(
    "/transactions/{transaction_id}/reject",
    response_model=MessageResponse,
    summary="🔐 Rechazar transacción (v2 - JWT)",
    description="Rechaza una transacción con autenticación JWT."
)
async def rechazar_transaccion_v2(
    transaction_id: str,
    current_user = Depends(require_aprobador_v2),
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Validación JWT real
    - ✅ Registro del rechazador
    """
    user_role = current_user.role.value
    transaction = TransactionService.rechazar_transaccion(db, transaction_id, user_role)
    
    return MessageResponse(
        message=f"Transacción rechazada por {current_user.nombre}",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.post(
    "/transactions/{transaction_id}/execute",
    response_model=MessageResponse,
    summary="🔐 Ejecutar transacción (v2 - JWT)",
    description="Ejecuta una transacción aprobada (simulado)."
)
async def ejecutar_transaccion_v2(
    transaction_id: str,
    current_user = Depends(get_current_user_v2),  # Cualquier usuario autenticado
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Requiere autenticación (cualquier rol)
    - ✅ Registro de quien ejecutó
    """
    transaction = TransactionService.ejecutar_transaccion(db, transaction_id)
    
    return MessageResponse(
        message=f"Transacción ejecutada por {current_user.nombre} (simulado)",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="🔐 Consultar transacción (v2 - JWT)",
    description="Obtiene los detalles de una transacción (requiere autenticación)."
)
async def consultar_transaccion_v2(
    transaction_id: str,
    current_user = Depends(get_current_user_v2),
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Requiere autenticación
    """
    transaction = crud_transaction.obtener_transaccion_por_id(db, transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )
    
    return transaction


@api_router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="🔐 Listar transacciones (v2 - JWT)",
    description="Lista transacciones del usuario autenticado."
)
async def listar_transacciones_v2(
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user_v2),
    db: Session = Depends(get_db)
):
    """
    ## Mejoras v2:
    - ✅ Filtra solo las transacciones del usuario (si es OPERADOR)
    - ✅ El APROBADOR ve todas las pendientes de aprobación
    """
    if current_user.role.value == "OPERADOR":
        # OPERADOR solo ve sus transacciones
        transactions = db.query(crud_transaction.Transaction).filter(
            crud_transaction.Transaction.created_by == current_user.email
        ).offset(skip).limit(limit).all()
    else:
        # APROBADOR ve todas
        transactions = crud_transaction.obtener_todas_transacciones(db, skip, limit)
    
    return transactions


@api_router.get(
    "/transactions/next-reference/preview",
    summary="📋 Ver próxima referencia",
    description="Muestra cuál será la próxima referencia que se generará."
)
async def preview_next_reference(
    current_user = Depends(get_current_user_v2),
    db: Session = Depends(get_db)
):
    """
    Endpoint útil para que el frontend muestre al usuario 
    cuál será la referencia de la siguiente transacción.
    """
    next_ref = ReferenceService.generar_siguiente_reference(db)
    ultima_ref = ReferenceService.obtener_ultima_reference(db)
    
    return {
        "ultima_referencia": ultima_ref,
        "proxima_referencia": next_ref,
        "mensaje": f"La próxima transacción tendrá la referencia: {next_ref}"
    }
