from sqlalchemy.orm import Session
from app.models.meal import mealLog
from app.schemas.meal_schema import MealLogCreate
from app.models.food import Food
from datetime import datetime, time, timezone
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


# The point of this function is to pull up every meal that the specific user has ever logged. for user's sake
def get_user_logs(db: Session, user_id: int):
    
    return db.query(mealLog).filter(mealLog.user_id == user_id).all()
    # SELECT * FROM meal_logs WHERE user_id = user_id
    #.all() is the secret part that converts this from a database cursor/call to a python list


def get_summary(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"Error": "User not found!"}
    
    user_targets = calculate_user_values(user)

    now = datetime.now(timezone.utc)
    dayStart = datetime.combine(now.date(), time.min, tzinfo = timezone.utc)
    dayEnd = datetime.combine(now.date(), time.max, tzinfo = timezone.utc)

    food_logs = (db.query(mealLog,Food).join(Food, mealLog.food_id == Food.fdc_id).filter(mealLog.user_id == user_id).filter(mealLog.created_at >= dayStart).filter(mealLog.created_at <= dayEnd).all())



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