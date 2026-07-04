import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from app.models.food import Food

#Holds the names of all the nutrients for reference/printing purposes
NUTRIENT_FEATURES = [
    "Protein", "Fats", "Carbs", "Calories",
    "calcium", "iron", "magnesium", "phosphorus", 
    "potassium", "sodium", "zinc", "selenium",
    "vitamin_a", "vitamin_e", "vitamin_c",
    "thiamin", "riboflavin", "niacin", "pantothenic_acid", 
    "vitamin_b6", "folate", "vitamin_b12"
]


# Global variables so that when things are extracted from the table, it's only done once
_FOOD_DF = None
_SCALED_MATRIX = None
_SCALER = None
_KNN_MODEL = None

def initialize_recommendation_engine(db: Session):
    
    global _FOOD_DF, _SCALED_MATRIX, _SCALER, _KNN_MODEL

    print("Loading Food Table and Nutrient Stuffs")

    query = db.query(Food)
    df = pd.read_sql(query.statement, db.bind)

    if df.empty:
        print("Database Empty Yo!")
        return
    
    df.set_index("fdc_id", inplace=True)
    _FOOD_DF = df

    feature_matrix = _FOOD_DF[NUTRIENT_FEATURES].fillna(0.0)

    _SCALER = StandardScaler()
    _SCALED_MATRIX = _SCALER.fit_transform(feature_matrix)

    _KNN_MODEL = NearestNeighbors(n_neighbors=6, metric="cosine", algorithm="brute")
    _KNN_MODEL.fit(_SCALED_MATRIX)

    print(f"{len(_FOOD_DF)} foods fitted")

def find_similar_foods(food_id: int, n_recommendations: int = 5) -> list[int]:
    
    global _FOOD_DF, _SCALED_MATRIX, _SCALER, _KNN_MODEL

    if _FOOD_DF is None or _KNN_MODEL is None:
        raise RuntimeError("Recommendation Engine not initialized")
    
    if food_id not in _FOOD_DF.index:
        print(f"Food id {food_id} not found in pre-compiled dataset")
        return []

    food_idx = _FOOD_DF.index.get_loc(food_id)

    food_vector = _SCALED_MATRIX[food_idx].reshape(1, -1)

    distances, indices = _KNN_MODEL.kneighbors(food_vector, n_neighbors=n_recommendations + 1)

    recommended_ids = _FOOD_DF.index[indices[0]].tolist()

    filtered_recs = [rid for rid in recommended_ids if rid != food_id]

    return filtered_recs[:n_recommendations]