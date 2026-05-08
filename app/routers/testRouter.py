#This file receives HTTP requests and sends them to testService.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.services import testService

router = APIRouter()
#The start to all router files. Different "themed" routers should go in separate files for good practice

@router.get("/search")
#Tells FastAPI that all GET Requests that have a "/search" is handled this way

def find_food(name: str, db: Session = Depends(get_db)):
    #name: str; Any URL that looks like "/search?name=str" is handled here
    #db: Session = Depends(get_db); tells FastAPI, before this entire function is run
    #get the, run the get_db function() from app.utils.db.py, to get the specific "conversation"
    #that we're going to be working on

    results = testService.search_food_items(db, name)
    #run our service function
    
    return results