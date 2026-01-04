from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas.transaction import TransactionCreate, TransactionResponse, MessageResponse
from services.transaction_service import TransactionService
from deps.auth import get_user_role, get_user_id
from deps.deps import get_db
import crud.transaction as crud_transaction


api_router = APIRouter(tags=["v1 - Transactions"])


@api_router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear transacción",
    description="Crea una nueva transacción. Solo usuarios con rol OPERADOR pueden crear transacciones.",
    responses={
        201: {
            "description": "Transacción creada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                        "reference": "PAY-001",
                        "amount": 1000.50,
                        "currency": "USD",
                        "status": "DRAFT",
                        "created_by": "op-001",
                        "approved_by": None,
                        "created_at": "2026-01-03T10:00:00",
                        "updated_at": "2026-01-03T10:00:00"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación - datos inválidos o referencia duplicada",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate_reference": {
                            "summary": "Referencia duplicada",
                            "value": {"detail": "Ya existe una transacción con la referencia 'PAY-001'"}
                        },
                        "invalid_amount": {
                            "summary": "Monto inválido",
                            "value": {"detail": "El monto debe ser mayor a cero"}
                        },
                        "invalid_currency": {
                            "summary": "Moneda inválida",
                            "value": {"detail": "La moneda debe tener exactamente 3 caracteres"}
                        }
                    }
                }
            }
        },
        403: {
            "description": "Rol no permitido - solo OPERADOR puede crear transacciones",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo usuarios con rol OPERADOR pueden crear transacciones"}
                }
            }
        }
    }
)
async def crear_transaccion(
    transaccion: TransactionCreate,
    user_role: str = Depends(get_user_role),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    ## Reglas:
    - Solo rol **OPERADOR** puede crear transacciones
    - La transacción se crea en estado **DRAFT**
    - El monto debe ser mayor a cero
    - La moneda debe tener exactamente 3 caracteres
    
    ## Headers requeridos:
    - `X-User-Role`: OPERADOR
    - `X-User-Id`: Identificador del operador
    """
    return TransactionService.crear_transaccion(db, transaccion, user_id, user_role)


@api_router.post(
    "/transactions/{transaction_id}/submit",
    response_model=MessageResponse,
    summary="Enviar a aprobación",
    description="Envía una transacción a aprobación. Solo OPERADOR puede ejecutar esta acción.",
    responses={
        200: {
            "description": "Transacción enviada a aprobación exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Transacción enviada a aprobación exitosamente",
                        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "PENDING_APPROVAL"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación - estado inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "La transacción debe estar en estado DRAFT para ser enviada a aprobación"}
                }
            }
        },
        403: {
            "description": "Rol no permitido - solo OPERADOR puede enviar a aprobación",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo usuarios con rol OPERADOR pueden enviar transacciones a aprobación"}
                }
            }
        },
        404: {
            "description": "Transacción no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Transacción no encontrada"}
                }
            }
        }
    }
)
async def enviar_a_aprobacion(
    transaction_id: str,
    user_role: str = Depends(get_user_role),
    db: Session = Depends(get_db)
):
    """
    ## Reglas:
    - Solo rol **OPERADOR** puede enviar a aprobación
    - El estado cambia de **DRAFT** a **PENDING_APPROVAL**
    - Solo transacciones en estado DRAFT pueden ser enviadas
    
    ## Headers requeridos:
    - `X-User-Role`: OPERADOR
    """
    transaction = TransactionService.enviar_a_aprobacion(db, transaction_id, user_role)
    return MessageResponse(
        message="Transacción enviada a aprobación exitosamente",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.post(
    "/transactions/{transaction_id}/approve",
    response_model=MessageResponse,
    summary="Aprobar transacción",
    description="Aprueba una transacción. Solo APROBADOR puede ejecutar esta acción.",
    responses={
        200: {
            "description": "Transacción aprobada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Transacción aprobada exitosamente",
                        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "APPROVED"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación - estado inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo se pueden aprobar transacciones en estado PENDING_APPROVAL"}
                }
            }
        },
        403: {
            "description": "Rol no permitido - solo APROBADOR puede aprobar",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo usuarios con rol APROBADOR pueden aprobar transacciones"}
                }
            }
        },
        404: {
            "description": "Transacción no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Transacción no encontrada"}
                }
            }
        }
    }
)
async def aprobar_transaccion(
    transaction_id: str,
    user_role: str = Depends(get_user_role),
    user_id: str = Depends(get_user_id),
    db: Session = Depends(get_db)
):
    """
    ## Reglas:
    - Solo rol **APROBADOR** puede aprobar
    - Solo se pueden aprobar transacciones en estado **PENDING_APPROVAL**
    - Al aprobar, el estado pasa a **APPROVED** y se registra el aprobador
    
    ## Headers requeridos:
    - `X-User-Role`: APROBADOR
    - `X-User-Id`: Identificador del aprobador
    """
    transaction = TransactionService.aprobar_transaccion(db, transaction_id, user_id, user_role)
    return MessageResponse(
        message="Transacción aprobada exitosamente",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.post(
    "/transactions/{transaction_id}/reject",
    response_model=MessageResponse,
    summary="Rechazar transacción",
    description="Rechaza una transacción. Solo APROBADOR puede ejecutar esta acción.",
    responses={
        200: {
            "description": "Transacción rechazada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Transacción rechazada",
                        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "REJECTED"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación - estado inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo se pueden rechazar transacciones en estado PENDING_APPROVAL"}
                }
            }
        },
        403: {
            "description": "Rol no permitido - solo APROBADOR puede rechazar",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo usuarios con rol APROBADOR pueden rechazar transacciones"}
                }
            }
        },
        404: {
            "description": "Transacción no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Transacción no encontrada"}
                }
            }
        }
    }
)
async def rechazar_transaccion(
    transaction_id: str,
    user_role: str = Depends(get_user_role),
    db: Session = Depends(get_db)
):
    """
    ## Reglas:
    - Solo rol **APROBADOR** puede rechazar
    - Solo se pueden rechazar transacciones en estado **PENDING_APPROVAL**
    - El estado pasa a **REJECTED** (estado final)
    
    ## Headers requeridos:
    - `X-User-Role`: APROBADOR
    """
    transaction = TransactionService.rechazar_transaccion(db, transaction_id, user_role)
    return MessageResponse(
        message="Transacción rechazada",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.post(
    "/transactions/{transaction_id}/execute",
    response_model=MessageResponse,
    summary="Ejecutar transacción",
    description="Ejecuta una transacción aprobada (simulado).",
    responses={
        200: {
            "description": "Transacción ejecutada exitosamente",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Transacción ejecutada exitosamente (simulado)",
                        "transaction_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "EXECUTED"
                    }
                }
            }
        },
        400: {
            "description": "Error de validación - estado inválido",
            "content": {
                "application/json": {
                    "example": {"detail": "Solo se pueden ejecutar transacciones en estado APPROVED"}
                }
            }
        },
        404: {
            "description": "Transacción no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Transacción no encontrada"}
                }
            }
        }
    }
)
async def ejecutar_transaccion(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    ## Reglas:
    - Solo transacciones en estado **APPROVED** pueden ejecutarse
    - Al ejecutar, el estado cambia a **EXECUTED**
    - La ejecución es **simulada** (sin integración externa)
    - No requiere autenticación específica
    """
    transaction = TransactionService.ejecutar_transaccion(db, transaction_id)
    return MessageResponse(
        message="Transacción ejecutada exitosamente (simulado)",
        transaction_id=transaction.transaction_id,
        status=transaction.status
    )


@api_router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    summary="Consultar transacción",
    description="Obtiene los detalles de una transacción por su ID."
)
async def consultar_transaccion(
    transaction_id: str,
    db: Session = Depends(get_db)
):
    """
    ## Descripción:
    Retorna toda la información de una transacción específica.
    
    No requiere autenticación para la consulta.
    """
    transaction = crud_transaction.obtener_transaccion_por_id(db, transaction_id)
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transacción no encontrada"
        )
    
    return transaction


# Endpoint adicional: Listar todas las transacciones (útil para testing)
@api_router.get(
    "/transactions",
    response_model=list[TransactionResponse],
    summary="Listar transacciones",
    description="Lista todas las transacciones (endpoint adicional para testing)."
)
async def listar_transacciones(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    ## Descripción:
    Endpoint adicional para listar todas las transacciones con paginación.
    Útil para pruebas y desarrollo.
    """
    return crud_transaction.obtener_todas_transacciones(db, skip=skip, limit=limit)
