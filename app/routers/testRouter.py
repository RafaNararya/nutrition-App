#This file receives HTTP requests and sends them to testService.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.services import testService

router = APIRouter()

@router.get("/search")
def find_food(name: str, db: Session = Depends(get_db)):
    results = testService.search_food_items(db, name)
    return results