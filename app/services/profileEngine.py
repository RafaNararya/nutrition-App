def calculate_user_values(User):
    if not all([User.age, User.gender, User.weight_kg, User.height_cm]):
        return {"error": "Profile Incomplete"}
    
    # bmr based on Mifflin - St Jeor Equation
    if User.gender.lower() == "male":
        bmr = (10 * User.weight_kg) + (6.25 * User.height_cm) - (5 * User.age) + 5
    else:
        bmr = (10 * User.weight_kg) + (6.25 * User.height_cm) - (5 * User.age) - 161

    multipliers = {
        "sedentary": 1.2,
        "lightly_active": 1.375,
        "moderately_active": 1.55,
        "heavily_active": 1.725
    }

    # Safely extract activity level whether it's stored as an Enum object or raw string
    activity_key = User.activity_level.value if hasattr(User.activity_level, 'value') else str(User.activity_level)
    target_calories = bmr * multipliers.get(activity_key, 1.2)

    # Standard Macro Splits (30% Protein, 40% Carbs, 30% Fats)
    target_protein = (target_calories * 0.30) / 4
    target_carbs = (target_calories * 0.40) / 4
    target_fats = (target_calories * 0.30) / 9

    # Clinical Micro-Nutrient RDA Mapping
    is_male = User.gender.lower() == "male"
    
    return {
        "macros": {
            "calories": round(target_calories, 0),
            "protein": round(target_protein, 1),
            "carbs": round(target_carbs, 1),
            "fats": round(target_fats, 1)
        },
        "minerals": {
            "calcium": 1000.0,
            "iron": 8.0 if is_male else 18.0,
            "magnesium": 400.0 if is_male else 310.0,
            "phosphorus": 700.0,
            "potassium": 3400.0 if is_male else 2600.0,
            "sodium": 2300.0,
            "zinc": 11.0 if is_male else 8.0,
            "selenium": 55.0
        },
        "b_vitamins": {
            "thiamin": 1.2 if is_male else 1.1,
            "riboflavin": 1.3 if is_male else 1.1,
            "niacin": 16.0 if is_male else 14.0,
            "pantothenic_acid": 5.0,
            "vitamin_b6": 1.3,
            "folate": 400.0,
            "vitamin_b12": 2.4
        },
        "antioxidants": {
            "vitamin_a": 900.0 if is_male else 700.0,
            "vitamin_c": 900.0 if is_male else 75.0,
            "vitamin_e": 15.0
        }
    }