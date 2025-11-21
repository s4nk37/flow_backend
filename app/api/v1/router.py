# app/api/v1/router.py
from fastapi import APIRouter
from app.api.v1.endpoints import todos_endpoint
from app.api.v1.endpoints import auth_endpoint
from app.api.v1.endpoints import users_endpoint

api_router = APIRouter()


@api_router.get("/")
def home():
    return {"message": "Flow Backend API is working 🚀"}


api_router.include_router(todos_endpoint.api_router, prefix="")
api_router.include_router(auth_endpoint.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_endpoint.router, prefix="/users", tags=["Users"])
