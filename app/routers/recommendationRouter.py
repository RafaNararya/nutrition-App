from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.food import Food
from app.services.recommendationEngine import find_similar_foods

router = APIRouter(prefix="/recommendations", tags=["Some Recommendations"])

@router.get("/substitute/{food_id}", status_code=status.HTTP_200_OK)
def get_food_substitutions(food_id: int, db: Session = Depends(get_db)):
    try:
        recommend_ids = find_similar_foods(food_id, n_recommendations=5)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = str(e)
        )
    
    if not recommend_ids:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Food Item with ID {food_id} not found in dattabase"
        )

    recommended_foods = db.query(Food).filter(Food.fdc_id.in_(recommend_ids)).all()

    id_to_food_map = {food.fdc_id: food for food in recommended_foods}
    ordered_recommendations = [id_to_food_map[rid] for rid in recommend_ids if rid in id_to_food_map]

    response_payload = []

    for food in ordered_recommendations:
        response_payload.append({
            "fdc_id": food.fdc_id,
            "food_name": food.description,
            "macros": {
                "protein": food.Protein,
                "fats": food.Fats,
                "carbs": food.Carbs,
                "calories": food.Calories,
                "calcium": food.calcium,
                "iron": food.iron,
                "magnesium": food.magnesium, 
                "phosphorus": food.phosphorus,
                "potassium": food.potassium,
                "sodium": food.sodium,
                "zinc": food.zinc,
                "selenium": food.selenium,
                "vitamin_a": food.vitamin_a,
                "vitamin_e": food.vitamin_e,
                "vitamin_c": food.vitamin_c,
                "thiamin": food.thiamin,
                "riboflavin": food.riboflavin,
                "niacin": food.niacin,
                "pantothenic_acid": food.pantothenic_acid,
                "vitamin_b6": food.vitamin_b6,
                "folate": food.folate,
                "vitamin_b12": food.vitamin_b12
            }
        })
    
    return {
        "source_food_id": food_id,
        "substitutions_found": len(response_payload),
        "reccommendations": response_payload
    }