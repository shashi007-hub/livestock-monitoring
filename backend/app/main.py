from fastapi import FastAPI
from contextlib import asynccontextmanager

from api.endpoints import router as api_router
from mqtt.client import start_mqtt
from db.database import Base, engine

Base.metadata.create_all(bind=engine)

# 👇 New: lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    # start_mqtt()
    yield
    # (Optional) Add shutdown logic here

app = FastAPI(title="Farm Management API", lifespan=lifespan)

app.include_router(api_router)
