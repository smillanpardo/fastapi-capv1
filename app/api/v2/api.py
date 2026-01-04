from fastapi import APIRouter
from api.v2 import transactions

api_router = APIRouter()

api_router.include_router(transactions.api_router)
