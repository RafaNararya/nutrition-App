from sqlalchemy.orm import Session
from app.models.food import Food

def search_food_items(db: Session, query_str: str, limit: int = 20):
    if not query_str or not query_str.strip():
        return []

    search_pattern = f"%{query_str.strip()}%"
    
    results = (
        db.query(Food)
        .filter(Food.description.ilike(search_pattern))
        .limit(limit)
        .all()
    )

    def fmt(val):
        """Safely rounds floats to 2 decimal places."""
        return round(float(val), 2) if val is not None else 0.0

    formatted_results = []
    for food in results:
        formatted_results.append({
            "fdc_id": food.fdc_id,
            "description": food.description,
            
            # Macros
            "Calories": fmt(getattr(food, "Calories", 0)),
            "Protein": fmt(getattr(food, "Protein", 0)),
            "Carbs": fmt(getattr(food, "Carbs", 0)),
            "Fats": fmt(getattr(food, "Fats", 0)),
            
            # Minerals
            "calcium": fmt(getattr(food, "calcium", 0)),
            "iron": fmt(getattr(food, "iron", 0)),
            "magnesium": fmt(getattr(food, "magnesium", 0)),
            "phosphorus": fmt(getattr(food, "phosphorus", 0)),
            "potassium": fmt(getattr(food, "potassium", 0)),
            "sodium": fmt(getattr(food, "sodium", 0)),
            "zinc": fmt(getattr(food, "zinc", 0)),
            "selenium": fmt(getattr(food, "selenium", 0)),

            # B-Complex
            "thiamin": fmt(getattr(food, "thiamin", 0)),
            "riboflavin": fmt(getattr(food, "riboflavin", 0)),
            "niacin": fmt(getattr(food, "niacin", 0)),
            "pantothenic_acid": fmt(getattr(food, "pantothenic_acid", 0)),
            "vitamin_b6": fmt(getattr(food, "vitamin_b6", 0)),
            "folate": fmt(getattr(food, "folate", 0)),
            "vitamin_b12": fmt(getattr(food, "vitamin_b12", 0)),

            # Antioxidants & Vitamins
            "vitamin_a": fmt(getattr(food, "vitamin_a", 0)),
            "vitamin_c": fmt(getattr(food, "vitamin_c", 0)),
            "vitamin_e": fmt(getattr(food, "vitamin_e", 0)),
        })

    return formatted_results