#Connection to FastAPI. FastAPI starter

from fastapi import FastAPI
from app.routers import testRouter

app = FastAPI()
app.include_router(testRouter.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Rafa's Nutrition App!"}

@app.get("/status")
def check_status():
    return {"Status": "Database is live", "Rows": 376}