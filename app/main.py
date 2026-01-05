from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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

# Configuración de CORS para permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",      # Frontend local (Vue/React dev)
        "http://localhost:3000",      # Frontend local (React default)
        "http://localhost:5173",      # Frontend local (Vite)
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "https://front-cap-nine.vercel.app"  # Frontend desplegado en Vercel (SIN /login)
    ],
    allow_credentials=True,
    allow_methods=["*"],              # Permite GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],              # Permite todos los headers (incluye X-User-Role, X-User-Id)
)

# Registrar ambas versiones
app.include_router(api_router_v1, prefix="/api/v1")
app.include_router(api_router_v2, prefix="/api/v2")

