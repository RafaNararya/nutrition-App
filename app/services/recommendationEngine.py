import numpy as np
import pandas as pd
from sqlalchemy.orm import Session
from sklearn.preprocessing import StandardScaler # Normalizes data so all nutrients are on the same scale
from sklearn.neighbors import NearestNeighbors # Machine learning model that is used to find "similar" items
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
# When the app starts up, it will populate once so that the server doesn't have to 
# query the DB and re-train the AI model every single time a user requests a recommendation
_FOOD_DF = None # Holds the Pandas DataFrame (the food data table)
_SCALED_MATRIX = None # Holds the nutrient data after it has been normalized
_SCALER = None # Holds the mathematical scaler object (needed)
_KNN_MODEL = None # Holds the trained nearest neighbors model

def initialize_recommendation_engine(db: Session):
    """Runs once when the server starts. It grabs the food data, prepares it, and then builds the recommendation model off of it"""

    # Tell python we want to modify the global variables declaread outside of this function
    global _FOOD_DF, _SCALED_MATRIX, _SCALER, _KNN_MODEL

    print("Loading Food Table and Nutrient Stuffs")

    # 1. Fetch Data from the Database
    query = db.query(Food) # Formulates a SQL Statement to select everythig from the Food Table
    df = pd.read_sql(query.statement, db.bind) #executes the query and converts the SQL rows into a Pandas Dataframe
    # query.statement converts a hihg level ORM query into a low-level SQLAlchemy Core Select Object
    # This core object contains the raw SQL Structure before it is sent to the database.
    # When pandas receives it, it can convert this object into a literal SQL String to execute
    # db.bind establishes a connection between SQLAlchemy and the actual database on Postgres

    # Safety Check: If the database has no foods, stop here to avoid crashing later
    if df.empty:
        print("Database Empty Yo!")
        return

    # 2. Prepare Data
    # Move the 'fdc_id' column of the datat rows and make it the row identifier (index)
    df.set_index("fdc_id", inplace=True)
    _FOOD_DF = df # cache this clean dataframe into our global variable

    # Extract just the nutrient columns. If any of the nutrients is missing, replace it with 0.0
    feature_matrix = _FOOD_DF[NUTRIENT_FEATURES].fillna(0.0)

    # 3. Scale Data
    # Machine learning algos struggle if one feature is 0-2000 (calories) and another is 0 - 0.0005 (vitamins)
    # The scale/number disparity is much too high for it to analyze
    # StandardScaler transforms number so they have a mean of 0 and a variance of 1
    _SCALER = StandardScaler()
    _SCALED_MATRIX = _SCALER.fit_transform(feature_matrix) # uses the scaling and transforms the numbers

    # 4. Train the AI Model
    # Choosing metric = cosine means we look at the ratio of nutrients rather than the absolute weights. Just a preference of relation
    # Algorithm = brute tells it to check every food option directly when finding matches
    _KNN_MODEL = NearestNeighbors(n_neighbors=6, metric="cosine", algorithm="brute")
    _KNN_MODEL.fit(_SCALED_MATRIX)

    print(f"{len(_FOOD_DF)} foods fitted")

def find_similar_foods(food_id: int, n_recommendations: int = 5) -> list[int]:
    """ takes a single food ID and returns a list of IDs for most similar foods"""
    
    global _FOOD_DF, _SCALED_MATRIX, _SCALER, _KNN_MODEL

    # Make sure that the setup function above actually ran
    if _FOOD_DF is None or _KNN_MODEL is None:
        raise RuntimeError("Recommendation Engine not initialized")
    # Make sure the requested food actually exists in our data
    if food_id not in _FOOD_DF.index:
        print(f"Food id {food_id} not found in pre-compiled dataset")
        return []
    #Find the numeric index (row position) of our specific food ID
    food_idx = _FOOD_DF.index.get_loc(food_id)

    # Pull the row of scaled nutrients for this food
    # .reshape(1, -1) converts it from a flat array into a 2D matrix layout because scikit needs 2D inputs
    food_vector = _SCALED_MATRIX[food_idx].reshape(1, -1)

    # Ask the model for the closest matches
    # Asking for (n_recommendations + 1) beacuse the absolute closest match to a food is ALWAYS itself
    distances, indices = _KNN_MODEL.kneighbors(food_vector, n_neighbors=n_recommendations + 1)
    
    # Look up the actual food IDs using the position indices returned by the model
    recommended_ids = _FOOD_DF.index[indices[0]].tolist()

    # Filter out the original food item so we don't recommend a banana to someone looking for a substitute for a banana
    filtered_recs = [rid for rid in recommended_ids if rid != food_id]

    # Return only the requested number of items, just in case filtering didn't work perfectly
    return filtered_recs[:n_recommendations]
