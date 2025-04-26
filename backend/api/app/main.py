from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from app.cron import my_cron_job
from pytz import timezone
from api.endpoints import router as api_router
from db.database import Base, engine

Base.metadata.create_all(bind=engine)


scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    ist = timezone('Asia/Kolkata')
    scheduler.add_job(my_cron_job, 'cron', hour=18, minute=00, timezone=ist)  
    scheduler.start()
    print("Scheduler started.")

    yield  # Run the app

    # Shutdown logic
    scheduler.shutdown()
    print("Scheduler shutdown.")

app = FastAPI(title="Farm Management API",lifespan=lifespan)

app.include_router(api_router)
