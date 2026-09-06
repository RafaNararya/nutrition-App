import os
from fastapi import FastAPI
from app.routers import testRouter, userRouter, mealRouter, recommendationRouter
from app.models import food, meal, user
from app.utils.db import Base, engine, sessionLocal
from contextlib import asynccontextmanager
from app.services.recommendationEngine import initialize_recommendation_engine
from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    db = sessionLocal()
    try:
        initialize_recommendation_engine(db)
        print(f"Recommendation Engine Initialized")
    except Exception as e:
        print(f"Failed to initialize recommendation engine: {e}")
    finally:
        db.close()
    
    yield


app = FastAPI(lifespan=lifespan)

# Read origins from an environment variable (comma-separated), or fall back to defaults
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS")

if ALLOWED_ORIGINS_ENV:
    origins = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",")]
else:
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(testRouter.router)
app.include_router(userRouter.router)
app.include_router(mealRouter.router)
app.include_router(recommendationRouter.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Rafa's Nutrition App"}

@app.get("/status")
def check_status():
    return {"Status": "Database is live", "Rows": 376}