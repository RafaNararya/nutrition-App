from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.food import Food
from app.services.recommendationEngine import find_similar_foods
from app.services.mealTracking import get_summary
from app.services.deficitEngine import recommend_deficit, calculate_deficit_vector

router = APIRouter(prefix="/recommendations", tags=["Some Recommendations"])

# Defines a GET request endpoint. {food_id} is a dynamic variable passed in the URL path.
@router.get("/substitute/{food_id}", status_code=status.HTTP_200_OK)
def get_food_substitutions(food_id: int, db: Session = Depends(get_db)):
    """API Endpoint that accepts a food_id, find substitutes, gets the details, and returns them"""
    try:
        # fire up the scikit model to get a list of raw integer IDs (of substitutions)
        recommend_ids = find_similar_foods(food_id, n_recommendations=5)

    except RuntimeError as e:
        # if the model was never initialized, send an exception back
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail = str(e)
        )

    # if list of recommend ids is empty, it means that whatever food_id we passed in doesn't exist in our data
    # because it should return substitutions, even if they were bad substitutions
    if not recommend_ids:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"Food Item with ID {food_id} not found in dattabase"
        )

    # Go back to the SQL database to fetch the human-readable names and details of those IDs
    # .in_() is the SQL equivalent of "WHERE id IN (123, 456, 789)"
    recommended_foods = db.query(Food).filter(Food.fdc_id.in_(recommend_ids)).all()

    # Databases don't guarantee they will return rows in the exact order we asked for them.
    # To fix this, we map the results into a quick dictionary { id: food_object }
    id_to_food_map = {food.fdc_id: food for food in recommended_foods}
    ordered_recommendations = [id_to_food_map[rid] for rid in recommend_ids if rid in id_to_food_map]

    # Make something that'll hold the clean data to send over the internet
    response_payload = []

    for food in ordered_recommendations:
        # Loop through each food object and map database table columns to an organized structure
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
    
    # Return the final API dictionary. FastAPI automatically turns this into JSON syntax.
    return {
        "source_food_id": food_id,
        "substitutions_found": len(response_payload),
        "reccommendations": response_payload
    }


@router.get("/deficit/{user_id}")
def get_deficit_recommendations(user_id: int, db: Session = Depends(get_db)):
    summary = get_summary(db, user_id)
    if "Error" in summary:
        raise HTTPException(status_code=404, detail=summary["Error"])
    
    recommendations = recommend_deficit(summary, limit=5)

    return {
        "user_id": user_id,
        "current_deficits": {
            k: round(v, 1) for k, v in calculate_deficit_vector(summary).items() if v > 0
        },
        "recommended_plugs": recommendations
    }