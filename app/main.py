#Connection to FastAPI. FastAPI starter

from fastapi import FastAPI
from services.testService import test_Function

app = FastAPI()

@app.get("/ping-db")
async def test():
    return test_Function()