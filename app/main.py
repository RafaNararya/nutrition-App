#Connection to FastAPI. FastAPI starter

from fastapi import FastAPI
from app.routers import testRouter, userRouter, mealRouter
from app.models import food, meal, user
from app.utils.db import Base, engine

app = FastAPI()
app.include_router(testRouter.router)
#.include_router("routerFileName".router): should be done for every new router file

app.include_router(userRouter.router)
app.include_router(mealRouter.router)

Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Rafa's Nutrition App!"}

@app.get("/status")
def check_status():
    return {"Status": "Database is live", "Rows": 376}