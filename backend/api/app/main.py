from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.endpoints import router as api_router
from db.database import Base, engine

Base.metadata.create_all(bind=engine)


app = FastAPI(title="Farm Management API")

app.include_router(api_router)
