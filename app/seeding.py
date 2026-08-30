import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from utils.db import engine

BASE_DIR = Path(__file__).resolve().parent
CSV_DIR = BASE_DIR / "csvFiles"

#Read all the information that's needed from the USDA CSVs
food = pd.read_csv(CSV_DIR / "food.csv")
foodNutrient = pd.read_csv(CSV_DIR / "food_nutrient.csv", low_memory=False)
nutrient = pd.read_csv(CSV_DIR / "nutrient.csv")
foodCategory = pd.read_csv(CSV_DIR / "food_category.csv")

#Highlight the nutrients needed (Calories, Carbs, Fats, Protein)
#Added: Micronutrient Panel (IDs based on their official USDA Database Keys)
macros = [1008, 1003, 1004, 1005]
minerals = [1087, 1089, 1090, 1091, 1092, 1093, 1095, 1103] # Ca, Fe, Mg, P, K, Na, Zn, Se
b_vitamins = [1165, 1166, 1167, 1170, 1175, 1177, 1178] # B1, B2, B3, B5, B6, B9, B12
antioxidants = [1106, 1109, 1162] # Vit A, Vit E, Vit C

# Combine all the lists into one list
targetNutrients = macros + minerals + b_vitamins + antioxidants

# Perform a high-efficiency row filtering operation.
# Evaluates whether the 'nutrient_id' column value matches an item in our master array.
filteredNutrients = foodNutrient[foodNutrient['nutrient_id'].isin(targetNutrients)]

# .pivot() restructures the tables. Originally, Every single value was its own column and the fdc_id just ran down the side 
# AFTER .pivot(), this makes it in the form of nutrient_id on the x axis while the fdc_id on the y axis, and the amount are what fills the table
# So it becomes something like, the fdc_id is just one food item in a row, while each column is the different macros/micros. Makes it nice to read and work with
# Right now though, the nutrient_id columns are just the ID number of the macro/micro instead of its actual names
pivotNutrients = filteredNutrients.pivot(index = "fdc_id", columns = "nutrient_id", values = "amount")


# Crucial Sorting Alignment: When Pandas executes .pivot(), it automatically sorts the 
# column headers in ascending numerical order based on the source integer IDs.
# Therefore, our manual column renaming array must perfectly mirror that sorted sequence.
# Turning the ID number macro/micro into its actual names
pivotNutrients.columns = [
    "Protein", "Fats", "Carbs", "Calories",  # Macros
    "calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc",  "selenium", # Minerals
    "vitamin_a", "vitamin_e", "vitamin_c",  # Antioxidants
    "thiamin", "riboflavin", "niacin", "pantothenic_acid", "vitamin_b6", "folate", "vitamin_b12"  # B-Vitamins
]

# Convert 'fdc_id' from an index back into a mutable data column for joining operations
# Basically adds another, far left column, that begins its indexing at 0
# just a secondary / primary (kind of confusing) indexing
pivotNutrients = pivotNutrients.reset_index()

foodCategory = foodCategory.rename(columns={"id": "food_category_id", "description": "food_group"})
food = pd.merge(food, foodCategory[["food_category_id", "food_group"]], on="food_category_id", how="left")

food["food_group"] = food["food_group"].fillna("Unknown")

# Execute an INNER JOIN between the descriptive dataset and our nutrient matrix.
# Discards any food item that lacks matching keys (fdc_id and description specifically) across both dataframes.
mergedPd = pd.merge(food[["fdc_id", "description", "food_group"]], pivotNutrients, on = "fdc_id", how="inner")

# Atwater General Factor System: Calculate proxy calorie estimations for entries 
# where the USDA left the Calorie field null. 
# Formula: (Protein * 4) + (Carbohydrates * 4) + (Fats * 9)
calculatedCalories = (mergedPd["Protein"] * 4 + mergedPd["Carbs"] * 4 + mergedPd["Fats"] * 9)

# Fill empty elements in the "Calories" column with our calculated vector array values.
# 'inplace=False' prevents direct memory override, making this a pure thread-safe mutation.
mergedPd["Calories"] = mergedPd["Calories"].fillna(calculatedCalories, axis = 0, inplace = False)

# Fill ALL micro columns with 0.0 so they don't break downstream mathematical math operations
micro_columns = [col for col in pivotNutrients.columns if col not in ["fdc_id", "Protein", "Fats", "Carbs", "Calories"]]

# Convert NaN (Not a Number) micro cells into 0.0 floats.
# This prevents backend calculation loops or mathematical aggregations from crashing due to null types.
mergedPd[micro_columns] = mergedPd[micro_columns].fillna(0.0)

#Drop any rows of foods that are missing more than one macro
minimizedTable = mergedPd.dropna(axis = 0, subset = ["Protein", "Fats", "Carbs" , "Calories"], thresh = 3, inplace = False)

# Housekeeping: Eliminate residual columns created during row splitting or data index resets.
if 'index' in minimizedTable.columns:
    minimizedTable = minimizedTable.drop(columns=['index'])
minimizedTable = minimizedTable.drop(columns=['food_category_id'], errors='ignore')
minimizedTable = minimizedTable.reset_index(drop=True) # drop=True prevents creating a new 'index' column


with engine.connect() as conn:
    # CRITICAL RELATIONAL STEP: 'CASCADE' instructs PostgreSQL to break the data shield.
    conn.execute(text("DROP TABLE IF EXISTS usda_foods CASCADE;"))
    conn.commit()
    print("Forced drop of usda_foods table completed.")

# Bulk insert the sanitized DataFrame into the database.
minimizedTable.to_sql('usda_foods', engine, if_exists='fail', index=False)
print("Database heavily re-seeded with extensive nutritional panels and food groups!")

# FIX: Add the Primary Key constraint to fdc_id so foreign keys can target it
with engine.connect() as conn:
    conn.execute(text("ALTER TABLE usda_foods ADD PRIMARY KEY (fdc_id);"))
    conn.commit()
    print("Primary key constraint added to usda_foods(fdc_id).")


