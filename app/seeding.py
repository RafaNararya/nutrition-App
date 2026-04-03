import pandas as pd
from sqlalchemy import create_engine

#Read all the information that's needed from the USDA CSVs
food = pd.read_csv("csvFiles/food.csv")
foodNutrient = pd.read_csv("csvFiles/food_nutrient.csv", low_memory = False)
nutrient = pd.read_csv("csvFiles/nutrient.csv")

#Highlight the nutrients needed (Calories, Carbs, Fats, Protein)
targetNutrients = [1008, 1003, 1004, 1005]
filteredNutrients = foodNutrient[foodNutrient['nutrient_id'].isin(targetNutrients)]

#Make fdc_id the thing that is the primary column so that later it can be merged easily with the other CSVs that have fdc_id in it
#Make new Columns with the macros
#Fix Columns
#Merge Nutrients and Food CSVs
pivotNutrients = filteredNutrients.pivot(index = "fdc_id", columns = "nutrient_id", values = "amount")
pivotNutrients.columns = ["Protein", "Fats", "Carbs", "Calories"]
pivotNutrients = pivotNutrients.reset_index()
mergedPd = pd.merge(food[["fdc_id", "description"]], pivotNutrients, on = "fdc_id", how="inner")

#Calculate Missing Calorie Values
calculatedCalories = (mergedPd["Protein"] * 4 + mergedPd["Carbs"] * 4 + mergedPd["Fats"] * 9)
mergedPd["Calories"] = mergedPd["Calories"].fillna(calculatedCalories, axis = 0, inplace = False)

#Drop any rows of foods that are missing more than one macro
minimizedTable = mergedPd.dropna(axis = 0, subset = ["Protein", "Fats", "Carbs" , "Calories"], thresh = 3, inplace = False)
minimizedTable = minimizedTable.reset_index()

#Send the Panda into Postgres
engine = create_engine("postgresql://nutrition_user:RafasNutrition1502@localhost:5432/nutrition_app")
minimizedTable.to_sql('usda_foods', engine, if_exists = 'replace', index = False)


