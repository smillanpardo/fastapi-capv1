from fastapi import APIRouter
from api.v1 import auth, transactions, setup

api_router = APIRouter()

api_router.include_router(auth.api_router, prefix="/auth")
api_router.include_router(transactions.api_router)
api_router.include_router(setup.router)
