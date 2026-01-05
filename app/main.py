from fastapi import FastAPI, Depends, HTTPException, status
from api.v1.api import api_router as api_router_v1
from api.v2.api import api_router as api_router_v2


app = FastAPI(
    title="API de Transacciones - Prueba Técnica Covalto",
    description="""
    ## API REST para flujo de autorización de transacciones financieras
    
    ### v1 - Versión Base (Prueba Técnica)
    - Autenticación por headers simples (X-User-Role, X-User-Id)
    - Reference manual
    
    ### v2 - Versión Empresarial (Valor Agregado)
    - Autenticación JWT real validando contra BD
    - Reference autogenerado consecutivo
    - Validación de usuarios con roles en BD
    """,
    version="2.0.0"
)

# Registrar ambas versiones
app.include_router(api_router_v1, prefix="/api/v1")
app.include_router(api_router_v2, prefix="/api/v2")

