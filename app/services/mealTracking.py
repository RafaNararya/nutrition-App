from sqlalchemy.orm import Session
from app.models.meal import mealLog
from app.schemas.meal_schema import MealLogCreate
from app.models.food import Food

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


def get_summary(db: Session, user_id: int):
    food_log = (db.query(mealLog, Food).join(Food, mealLog.food_id == Food.fdc_id).filter(mealLog.user_id == user_id).all())

    summary = {
        "total calories": 0.0,
        "total protein": 0.0,
        "total fats": 0.0,
        "total carbs": 0.0,
        "meals logged": []
    }

    for log, food in food_log:
        grams = log.quantity_grams

        calories = (food.Calories / 100) * grams
        protein = (food.Protein / 100) * grams
        carbs = (food.Carbs / 100) * grams
        fats = (food.Fats / 100) * grams

        summary["total calories"] += calories
        summary["total protein"] += protein
        summary["total carbs"] += carbs
        summary["total fats"] += fats

        summary["meals logged"].append({
            "id": log.id,
            "grams": grams, 
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats
        })

    return summary