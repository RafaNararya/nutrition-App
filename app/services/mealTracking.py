from sqlalchemy.orm import Session
from app.models.meal import mealLog
from app.schemas.meal_schema import MealLogCreate

def log_meal(db: Session, meal_data: MealLogCreate):
    new_log = mealLog(
        user_id = meal_data.user_id,
        food_id = meal_data.food_id,
        quantity_grams = meal_data.quantity_grams
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

def get_user_logs(db: Session, user_id: int):
    return db.query(mealLog).filter(mealLog.user_id == user_id).all()