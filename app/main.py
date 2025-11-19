from fastapi import FastAPI
from app.api.v1.router import api_router
from app.database.session import engine, Base


Base.metadata.create_all(bind=engine)

app = FastAPI(title="Flow Todo API")

app.include_router(api_router, prefix="/api/v1")
