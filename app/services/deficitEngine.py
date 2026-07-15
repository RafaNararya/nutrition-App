import numpy as np
import pandas as pd
from app.services import recommendationEngine
from app.services.recommendationEngine import NUTRIENT_FEATURES

def calculate_deficit_vector(summary_payload: dict) -> dict:
    """
    Takes the daily summary dictionary from "get_summary" and subtracts them to find out what is missing
    Any overshot values are immediately truncated to 0.0.
    """
    targets = summary_payload.get("targets", {})
    logged = summary_payload.get("logged_totals", {})

    deficit = {}
    flat_targets = {}
    flat_logged = {}

    for panel in ["macros", "minerals", "b_vitamins", "antioxidants"]:
        flat_targets.update(targets.get(panel, {}))
        flat_logged.update(logged.get(panel, {}))

    for nutrient in NUTRIENT_FEATURES:
        nutrient_lower = nutrient.lower()
        t_val = flat_targets.get(nutrient_lower, 0.0)
        l_val = flat_logged.get(nutrient_lower, 0.0)

        deficit[nutrient] = max(0.0, t_val - l_val)

    return deficit

def recommend_deficit(summary_payload: dict, limit: int = 5) -> list[dict]:
    """
    Evaluates the daily nutrient gaps and matches them against the unscaled database values to find foods that bridge the gap
    """

    food_df = recommendationEngine._FOOD_DF

    if food_df is None:
        raise RuntimeError("Recommendation Engine gotta be up")
    
    deficit_vector = calculate_deficit_vector(summary_payload)

    target_array = np.array([deficit_vector[feature] for feature in NUTRIENT_FEATURES])

    if np.sum(target_array) == 0:
        return []
    
    feature_matrix = food_df[NUTRIENT_FEATURES].fillna(0.0).values

    weights = np.ones(len(NUTRIENT_FEATURES))
    weights[0:4] = 15.0

    differences = feature_matrix - target_array
    weighted_diffs = differences * weights
    distances = np.linalg.norm(weighted_diffs, axis=1)

    closest_indices = np.argsort(distances)

    results = []
    for idx in closest_indices[:limit]:
        fdc_id = food_df.index[idx]
        food_row = food_df.iloc[idx]
        results.append({
            "fdc_id": int(fdc_id),
            "description": food_row["description"],
            "culinary_group": food_row["culinary_group"],
            "match_score": float(distances[idx]),
            # Quick snapshot of what this food offers per 100g to show on the card
            "macros_per_100g": {
                "calories": float(food_row["Calories"]),
                "protein": float(food_row["Protein"]),
                "carbs": float(food_row["Carbs"]),
                "fats": float(food_row["Fats"])
            }
        })
    
    return results