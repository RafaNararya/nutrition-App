import pandas as pd
from sqlalchemy import create_engine, text

#Read all the information that's needed from the USDA CSVs
food = pd.read_csv("csvFiles/food.csv")
foodNutrient = pd.read_csv("csvFiles/food_nutrient.csv", low_memory = False)
nutrient = pd.read_csv("csvFiles/nutrient.csv")

#Highlight the nutrients needed (Calories, Carbs, Fats, Protein)
#Added: Micronutrient Panel
macros = [1008, 1003, 1004, 1005]
minerals = [1087, 1089, 1090, 1091, 1092, 1093, 1095, 1103] # Ca, Fe, Mg, P, K, Na, Zn, Se
b_vitamins = [1165, 1166, 1167, 1170, 1175, 1177, 1178] # B1, B2, B3, B5, B6, B9, B12
antioxidants = [1106, 1109, 1162] # Vit A, Vit E, Vit C

targetNutrients = macros + minerals + b_vitamins + antioxidants
filteredNutrients = foodNutrient[foodNutrient['nutrient_id'].isin(targetNutrients)]

#Make fdc_id the thing that is the primary column so that later it can be merged easily with the other CSVs that have fdc_id in it
#Make new Columns with the macros
#Fix Columns
#Merge Nutrients and Food CSVs
pivotNutrients = filteredNutrients.pivot(index = "fdc_id", columns = "nutrient_id", values = "amount")


pivotNutrients.columns = [
    "Protein", "Fats", "Carbs", "Calories",  # Macros
    "calcium", "iron", "magnesium", "phosphorus", "potassium", "sodium", "zinc",  "selenium", # Minerals
    "vitamin_a", "vitamin_e", "vitamin_c",  # Antioxidants
    "thiamin", "riboflavin", "niacin", "pantothenic_acid", "vitamin_b6", "folate", "vitamin_b12"  # B-Vitamins
]

pivotNutrients = pivotNutrients.reset_index()
mergedPd = pd.merge(food[["fdc_id", "description"]], pivotNutrients, on = "fdc_id", how="inner")

#Calculate Missing Calorie Values
calculatedCalories = (mergedPd["Protein"] * 4 + mergedPd["Carbs"] * 4 + mergedPd["Fats"] * 9)
mergedPd["Calories"] = mergedPd["Calories"].fillna(calculatedCalories, axis = 0, inplace = False)

# Fill ALL micro columns with 0.0 so they don't break downstream mathematical math operations
micro_columns = [col for col in pivotNutrients.columns if col not in ["fdc_id", "Protein", "Fats", "Carbs", "Calories"]]
mergedPd[micro_columns] = mergedPd[micro_columns].fillna(0.0)

#Drop any rows of foods that are missing more than one macro
minimizedTable = mergedPd.dropna(axis = 0, subset = ["Protein", "Fats", "Carbs" , "Calories"], thresh = 3, inplace = False)
if 'index' in minimizedTable.columns:
    minimizedTable = minimizedTable.drop(columns=['index'])
minimizedTable = minimizedTable.reset_index()

#Send the Panda into Postgres
engine = create_engine("postgresql://nutrition_user:RafasNutrition1502@localhost:5432/nutrition_app")

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS usda_foods CASCADE;"))
    conn.commit()
    print("Forced drop of usda_foods table completed.")


minimizedTable.to_sql('usda_foods', engine, if_exists = 'fail', index = False)
print("Database heavily re-seeded with extensive nutritional panels!")


