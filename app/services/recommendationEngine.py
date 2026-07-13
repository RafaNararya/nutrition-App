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

CULINARY_MAPPING = {
    "Poultry Products": "Animal_Protein",
    "Beef Products": "Animal_Protein",
    "Pork Products": "Animal_Protein",
    "Finfish and Shellfish Products": "Animal_Protein",
    "Dairy and Egg Products": "Animal_Protein",
    "Grains and Pasta": "Whole_Grains_Carbs",
    "Cereal Grains": "Whole_Grains_Carbs",
    "Vegetables and Vegetable Products": "Produce_Vegetables",
    "Fruits and Fruit Juices": "Produce_Fruits",
    "Legumes and Legume Products": "Plant_Protein_Carbs",
    "Nut and Seed Products": "Fats_Seeds"
}

# Global variables so that when things are extracted from the table, it's only done once
# When the app starts up, it will populate once so that the server doesn't have to 
# query the DB and re-train the AI model every single time a user requests a recommendation
_FOOD_DF = None             # Holds the master Pandas DataFrame with culinary columns added
_GROUP_MODELS = {}          # Dictionary holding separate trained KNN models per group: {group_name: KNN_model}
_GROUP_SCALERS = {}         # Dictionary holding separate fitted Scalers per group: {group_name: Scaler_object}
_GROUP_MATRICES = {}        # Dictionary holding separate scaled feature matrices: {group_name: matrix}

def initialize_recommendation_engine(db: Session):
    """Runs once when the server starts. It grabs the food data, prepares it, and then builds the recommendation model off of it"""

    # Tell python we want to modify the global variables declaread outside of this function
    global _FOOD_DF, __GROUP_MODELS, _GROUP_SCALERS, _GROUP_MATRICES

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

    # Force in a new column of the table "Culinary_Group" using
    # The relationships in culinary_mapping
    df['culinary_group'] = df['food_group'].map(CULINARY_MAPPING).fillna("Other")

    # Solve the Rice vs. Flour problem using case-insensitive regex matching
    baking_keywords = r'flour|powder|starch|mix|blend'
    is_grain = df['culinary_group'] == 'Whole_Grains_Carbs'
    has_baking_keyword = df['description'].str.contains(baking_keywords, case=False, na=False)

    # Re-route flours and baking ingredients into their own isolated group
    df.loc[is_grain & has_baking_keyword, 'culinary_group'] = 'Baking_Ingredients'
    
    _FOOD_DF = df # cache this clean dataframe into our global variable

    # Reset tracking objects to prevent stale states on hot-reload
    _GROUP_MODELS.clear()
    _GROUP_SCALERS.clear()
    _GROUP_MATRICES.clear()

    # 3. Train isolated models for each unique culinary group
    unique_groups = _FOOD_DF['culinary_group'].unique()
    
    for group in unique_groups:
        # Filter dataframe down to just this group's rows
        group_df = _FOOD_DF[_FOOD_DF['culinary_group'] == group]
        
        # Pull out nutrient numbers and fill any missing gaps with zero
        feature_matrix = group_df[NUTRIENT_FEATURES].fillna(0.0)
        
        # We need at least 2 items in a group to recommend something other than itself safely
        if len(group_df) < 2:
            continue

        # Scale the features specifically relative to this group's norms
        scaler = StandardScaler()
        scaled_matrix = scaler.fit_transform(feature_matrix)
        
        # Fit a group-specific KNN model
        knn_model = NearestNeighbors(metric="cosine", algorithm="brute")
        knn_model.fit(scaled_matrix)
        
        # Cache objects into our global group dictionaries
        _GROUP_SCALERS[group] = scaler
        _GROUP_MATRICES[group] = scaled_matrix
        _GROUP_MODELS[group] = knn_model
        
        print(f" -> Cluster '{group}': Fitted {len(group_df)} foods")

    print(f"{len(_FOOD_DF)} foods fitted")

def find_similar_foods(food_id: int, n_recommendations: int = 5) -> list[int]:
    """ takes a single food ID and returns a list of IDs for most similar foods"""
    
    global _FOOD_DF, __GROUP_MODELS, _GROUP_SCALERS, _GROUP_MATRICES

    # Make sure that the setup function above actually ran
    if _FOOD_DF is None or _KNN_MODEL is None:
        raise RuntimeError("Recommendation Engine not initialized")
    # Make sure the requested food actually exists in our data
    if food_id not in _FOOD_DF.index:
        print(f"Food id {food_id} not found in pre-compiled dataset")
        return []

    # Find what culinary group the target food is in:
    target_food = _FOOD_DF.loc[food_id]
    group = target_food['culinary_group']

    if group not in _GROUP_MODELS:
        print(f"No recommendation sub-model available for group cluster: {group}")
        return []

    # isolate the data structures assigned to this specific group
    group_df = _FOOD_DF[_FOOD_DF['culinary_group'] == group]
    scaler = _GROUP_SCALERS[group]
    scaled_matrix = _GROUP_MATRICES[group]
    knn_model = _GROUP_MODELS[group]

    # find the position of our food within this group's localized matrix
    group_local_idx = group_df.index.get_loc(food_id)
    food_vector = scaled_matrix[group_local_idx].reshape(1, -1)
    
    # Query the group-restricted model
    # dynamically cap neighbors requested based on total group size to prevent out-of-bounds requests
    max_neighbors = min(n_recommendations + 1, len(group_df))
    distances, indices = knn_model.kneighbors(food_vector, n_neighbors=max_neighbors)

    # Map localized row positions back to actual database fdc_ids
    recommended_ids = group_df.index[indices[0]].tolist()

    # Filter out the source item itself
    filtered_recs = [rid for rid in recommended_ids if rid != food_id]

    return filtered_recs[:n_recommendations]
