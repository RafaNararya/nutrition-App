# In your food/search route or service function
from sqlalchemy.orm import Session
from app.models.food import Food

def search_food_items(db: Session, query_str: str, limit: int = 20):
    if not query_str or not query_str.strip():
        return []

    # ILIKE ensures 'Egg' matches 'egg', 'EGG', or 'Egg, white, raw'
    search_pattern = f"%{query_str.strip()}%"
    
    results = (
        db.query(Food)
        .filter(Food.description.ilike(search_pattern))
        .limit(limit)
        .all()
    )

    # Format output keys to match what FoodSearch.jsx expects
    formatted_results = []
    for food in results:
        formatted_results.append({
            "fdc_id": food.fdc_id,
            "description": food.description,
            "Calories": getattr(food, "Calories", 0.0) or 0.0,
            "Protein": getattr(food, "Protein", 0.0) or 0.0,
            "Carbs": getattr(food, "Carbs", 0.0) or 0.0,
            "Fats": getattr(food, "Fats", 0.0) or 0.0,
        })

    return formatted_results