from sqlalchemy.orm import Session
from app.models.meal import mealLog
from app.schemas.meal_schema import MealLogCreate

def log_meal(db: Session, meal_data: MealLogCreate):
    # Taking the stuff out of the JSON from the Schema and converting it to something Postgres can read 
    new_log = mealLog(
        user_id = meal_data.user_id,
        food_id = meal_data.food_id,
        quantity_grams = meal_data.quantity_grams
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log

# The point of this function is to pull up every meal that the specific user has ever logged. for user's sake
def get_user_logs(db: Session, user_id: int):
    return db.query(mealLog).filter(mealLog.user_id == user_id).all()
    # SELECT * FROM meal_logs WHERE user_id = user_id
    #.all() is the secret part that converts this from a database cursor/call to a python list