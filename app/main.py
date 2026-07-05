#Connection to FastAPI. FastAPI starter

from fastapi import FastAPI
from app.routers import testRouter, userRouter, mealRouter, recommendationRouter
from app.models import food, meal, user
from app.utils.db import Base, engine, sessionLocal
from contextlib import asynccontextmanager
from app.services.recommendationEngine import initialize_recommendation_engine

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
app.include_router(testRouter.router)
#.include_router("routerFileName".router): should be done for every new router file

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