import numpy as np
import pandas as pd
from app.services import recommendationEngine
from app.services.recommendationEngine import NUTRIENT_FEATURES

def calculate_deficit_vector(summary_payload: dict) -> dict:
    """
    Takes the daily summary dictionary from "get_summary" and subtracts them to find out what is missing
    Any overshot values are immediately truncated to 0.0.
    """

    # Get the goals and logged totals (actual eaten) from the payload.
    # If those keys dont exist, default to an empty dict to prevent crashing
    # these are read from the get_summary function
    targets = summary_payload.get("targets", {})
    logged = summary_payload.get("panels",{})

    deficit = {}
    flat_targets = {}
    flat_logged = {}

    # flatten the nested data structure
    # The database payload (get_summary) organizes nutrients into sub-panels: macros, minerals, b_vitamins, and antioxidants
    # We loop through each panel and merge all of them into single flat dictionaries so they are easier to read
    for panel in ["macros", "minerals", "b_vitamins", "antioxidants"]:
        flat_targets.update(targets.get(panel, {}))
        flat_logged.update(logged.get(panel, {}))

    # calculate the gap between each of the 22 tracked macros/micros
    for nutrient in NUTRIENT_FEATURES:

        nutrient_lower = nutrient.lower()
        # Convert nutrient name to lowercase because the JSON payload uses lowercase

        # Grab the values if a nutrient isn't listed, default to 0.0
        target_val = flat_targets.get(nutrient_lower, 0.0)
        logged_val = flat_logged.get(nutrient_lower, 0.0)

        # Core logic: Target - Logged = Deficit.
        # "max(0.0, ...)" ensures that if the user ate *more* of a nutrient than their target
        # (resulting in a negative number), we round it up to 0.0. 
        # We only care about what they are missing, not what they overshot
        deficit[nutrient] = max(0.0, target_val - logged_val)

    return deficit

def recommend_deficit(summary_payload: dict, limit: int = 5) -> list[dict]:
    """
    Evaluates the daily nutrient gaps and matches them against the unscaled database values to find foods that bridge the gap
    """

    # Get the cached DF we loaded during the startup in the recommendationEngine
    # This lets us work with a static DF instead of querying the database over and over again which
    # would be expensive in the efficiency department
    food_df = recommendationEngine._FOOD_DF

    # if recommendationEngine isn't loaded yet, no recommendations, let alone deficits be offered
    if food_df is None:
        raise RuntimeError("Recommendation Engine gotta be up")

    # Calculate what things the user is missing today (remember that get_summary is based on daily meal logs)
    deficit_vector = calculate_deficit_vector(summary_payload)

    # Convert that dictionary of missing nutrients into a flat, ordered list (array)
    # This must be in the exact same order as NUTRIENT_FEATURES so the math lines up
    target_array = np.array([deficit_vector[feature] for feature in NUTRIENT_FEATURES])

    # Super niche safety net where the user has hit all of their goals which means we recommend nothing for their nonexistent deficit
    if np.sum(target_array) == 0:
        return []

    # Extract the database nutrient matrix
    # This creates a big 2D table of numbers for all foods, substituting any missing values with 0.0
    feature_matrix = food_df[NUTRIENT_FEATURES].fillna(0.0).values

    # Apply Weights
    # This is a crucial step. Without weights, a food with 10mg of Calcium might look "closer" 
    # to your target than a food with 300 Calories because the calorie number is so much larger
    # We start by giving every nutrient a weight multiplier of 1.0
    weights = np.ones(len(NUTRIENT_FEATURES))

    # We heavily boost the first 4 items (Protein, Fats, Carbs, Calories) to 15.0
    # This tells our algorithm: Prio hitting your macro targets 15 times more than your vitamins
    weights[0:4] = 15.0


    # Calculate the "Distance" between our target gaps and every food's nutrients.
    # Mathematically:
    #   - Subtract the user's target gap from every food row.
    #   - Multiply the result by our weights.
    #   - Find the Euclidean Norm (a multi-dimensional distance formula) for each row.
    differences = feature_matrix - target_array
    weighted_diffs = differences * weights
    distances = np.linalg.norm(weighted_diffs, axis=1)

    # Sort the results.
    # np.argsort does not sort the actual values; it returns the indices (row positions)
    # that *would* sort the list from smallest distance (best match) to largest (worst match)
    closest_indices = np.argsort(distances)

    results = []
    for idx in closest_indices[:limit]:
        fdc_id = food_df.index[idx]
        food_row = food_df.iloc[idx]
        results.append({
            "fdc_id": int(fdc_id),
            "description": food_row["description"],
            "culinary_group": food_row["culinary_group"],
            "match_score": float(distances[idx]), # Lower score = closer fit to the target gap

            # Quick snapshot of what this food offers per 100g to show on the card
            "macros_per_100g": {
                "calories": float(food_row["Calories"]),
                "protein": float(food_row["Protein"]),
                "carbs": float(food_row["Carbs"]),
                "fats": float(food_row["Fats"])
            }
        })
    
    return results