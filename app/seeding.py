import pandas as pd

food = pd.read_csv("csvFiles/food.csv")
foodNutrient = pd.read_csv("csvFiles/food_nutrient.csv")
nutrient = pd.read_csv("csvFiles/nutrient.csv")

targetNutrients = [1008, 1003, 1004, 1005]
filteredNutrients = foodNutrient[foodNutrient['nutrient_id'].isin(targetNutrients)]

pivotNutrients = filteredNutrients.pivot(index = "fdc_id", columns = "nutrient_id", values = "amount")
pivotNutrients.columns = ["Protein", "Fats", "Carbs", "Calories"]
pivotNutrients = pivotNutrients.reset_index()
mergedPd = pd.merge(food[["fdc_id", "description"]], pivotNutrients, on = "fdc_id", how="inner")
minimizedTable = mergedPd.dropna(axis = 0, subset = ["Protein", "Fats", "Carbs" , "Calories"], inplace = False)
minimizedTable = minimizedTable.reset_index()
print(pivotNutrients)
print(mergedPd)
print(minimizedTable)