from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session 
from app.utils.db import get_db
from app.schemas.meal_schema import MealLogCreate, MealLogOut
from app.services import mealTracking

router = APIRouter(prefix="/meals", tags=["Meals"])

@router.post("/", response_model=MealLogOut)
def record_meal(meal: MealLogCreate, db: Session = Depends(get_db)):
    return mealTracking.log_meal(db = db, meal_data = meal)

@router.get("/{user_id}", response_model=list[MealLogOut])
def view_user_logs(user_id: int, db: Session = Depends(get_db)):
    return mealTracking.get_user_logs(db = db, user_id=user_id)