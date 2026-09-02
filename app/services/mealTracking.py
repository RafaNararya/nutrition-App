from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.meal import mealLog
from app.schemas.meal_schema import MealLogCreate
from app.models.food import Food
from datetime import datetime, timezone
from app.models.user import User
from app.services.profileEngine import calculate_user_values

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

def delete_meal(db: Session, meal_log_id: int, user_id: int) -> bool:
    
    #Attempts to find a specific meal log belonging to a user and deletes it.
    #Returns True if successful, False if the record wasn't found.
    
    db_item = db.query(mealLog).filter(
        mealLog.id == meal_log_id, 
        mealLog.user_id == user_id
    ).first()
    
    if not db_item:
        return False
        
    db.delete(db_item)
    db.commit()
    return True

# 1. UPDATED: Fetches ONLY TODAY'S logs for the main dashboard
def get_user_logs(db: Session, user_id: int):
    today = datetime.now(timezone.utc).date()

    # SELECT meal_logs.*, usda_foods.description AS food_name FROM meal_logs JOIN usda_foods ON meal_logs.food_id = usda_foods.fdc_id WHERE user_id = user_id
    results = (
        db.query(mealLog, Food.description.label("food_name"))
        .join(Food, mealLog.food_id == Food.fdc_id)
        .filter(mealLog.user_id == user_id)
        .filter(func.date(mealLog.created_at) == today)
        .order_by(mealLog.created_at.desc())
        .all()
    )


    # Map into a JSON-serializable structure including food_name for front-end rendering
    logs = []
    for log, food_name in results:
        logs.append({
            "id": log.id,
            "user_id": log.user_id,
            "food_id": log.food_id,
            "quantity_grams": log.quantity_grams,
            "created_at": log.created_at,
            "food_name": food_name
        })

    #.all() is the secret part that converts this from a database cursor/call to a python list    
    return logs


# Fetches UNIQUE past foods for quick re-logging (deduplicated by food_id)
def get_user_history(db: Session, user_id: int):
    # Order logs descending by creation time
    all_logs = (
        db.query(mealLog, Food.description.label("food_name"))
        .join(Food, mealLog.food_id == Food.fdc_id)
        .filter(mealLog.user_id == user_id)
        .order_by(mealLog.created_at.desc())
        .all()
    )
    
    seen_foods = set()
    history = []
    
    for log, food_name in all_logs:
        if log.food_id not in seen_foods:
            seen_foods.add(log.food_id)
            history.append({
                "id": log.id,
                "user_id": log.user_id,
                "food_id": log.food_id,
                "quantity_grams": log.quantity_grams,
                "created_at": log.created_at,
                "food_name": food_name
            })
            
    return history


def get_summary(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"Error": "User not found!"}
    
    user_targets = calculate_user_values(user)

    today = datetime.now(timezone.utc).date()

    # Query today's logs using func.date to match server and database date bounds
    food_logs = (
        db.query(mealLog, Food)
        .join(Food, mealLog.food_id == Food.fdc_id)
        .filter(mealLog.user_id == user_id)
        .filter(func.date(mealLog.created_at) == today)
        .all()
    )


    # Group columns by logical front-end presentation panels.
    # CRITICAL MECHANICAL REQUIREMENT: The string elements in these arrays must exactly 
    # match the sensitive-case variable names declared in your SQLAlchemy 'Food' class map.
    panels = {
        "macros": ["Calories", "Protein", "Carbs", "Fats"],
        "minerals": ["calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc", "selenium"],
        "b_vitamins": ["thiamin", "riboflavin", "niacin", "pantothenic_acid", "vitamin_b6", "folate", "vitamin_b12"],
        "antioxidants": ["vitamin_a", "vitamin_c", "vitamin_e"]
    }

    # 2. Data Structure Initialization:
    # We initialize an in-memory dictionary. This is the structural draft of the JSON 
    # response that your future React frontend will parse to display the dashboard.
    # Dynamically allocate memory structures for the response payload using nested dictionary comprehension.
    # Coercing nutrient strings to lowercase prevents case-mismatch processing bugs on the client-side/frontend application layer.
    summary = {
        "targets": user_targets,
        "panels": {panel_name: {nut.lower(): 0.0 for nut in nut_list} for panel_name, nut_list in panels.items()},
        "meals_logged": [] # A nested array to hold the itemized breakdown
    }


    # 3. The Math Engine Loop:
    # We unpack each tuple from our SQL result. 'log' gives us the user's portion size; 
    # 'food' gives us the baseline USDA macro values.
    # Iterate through the returned cursor tuple array.
    for log, food in food_logs:
        grams = log.quantity_grams

        # Initialize an isolated JSON-serializable hash map structure for this unique meal item
        meal_item = {
            "id": log.id,
            "food_name": food.description,  # Available for easy front-end display!
            "grams": grams,
            "panels": {panel_name: {} for panel_name in panels}
        }

        # Accumulation (Reduction):
        # We add the scaled numbers directly into our running tallies inside the dictionary.
        # Dynamically loop through every panel list and run the math formula
        for panel_name, nutrient_list in panels.items():
            for nutrient in nutrient_list:
                # getattr(food, "Protein") acts exactly like food.Protein dynamically
                raw_value = getattr(food, nutrient, 0.0) or 0.0
                calculated_value = round((raw_value / 100) * grams, 2)
                
                # Assign to this specific meal's snapshot
                meal_item["panels"][panel_name][nutrient.lower()] = calculated_value
                
                # Add to the global running daily total for the panel
                summary["panels"][panel_name][nutrient.lower()] += calculated_value


        # DTO (Data Transfer Object) Mapping:
        # We append a customized, human-readable dictionary to our list. Notice we use Python's 
        # round() function to 1 decimal place. This keeps the data payload "clean" so you aren't 
        # passing long floating-point anomalies (like 42.10000000004) over the internet.
        summary["meals_logged"].append(meal_item)
    for panel_name in summary["panels"]:
        summary["panels"][panel_name] = {k: round(v, 1) for k, v in summary["panels"][panel_name].items()}

    return summary