from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session 
from app.utils.db import get_db
from app.schemas.meal_schema import MealLogCreate, MealLogOut
from app.services import mealTracking

# prefix="/meals" means all these routes start with yourdomain.com/meals/
router = APIRouter(prefix="/meals", tags=["Meals"])

# As a reminder, response_model follows the output class that was defined in the schemas.
@router.post("/", response_model=MealLogOut)
def record_meal(meal: MealLogCreate, db: Session = Depends(get_db)):
    # This is a standard POST Pattern: Take Data -> Hand to Service to do whatever -> then Return the result
    return mealTracking.log_meal(db = db, meal_data = meal)

# response_model = list[MealLogOut]
# Since a user can have many meals, we tell FastAPI to expect an array/list of meal objects
@router.get("/{user_id}", response_model=list[MealLogOut])
def view_user_logs(user_id: int, db: Session = Depends(get_db)):
    # {user_id} is a Path Parameter. Whatever the user types in the URL 
    # (e.g., /meals/1) gets passed into the function as the variable 'user_id'.
    return mealTracking.get_user_logs(db = db, user_id=user_id)

# NEW: Returns ALL-TIME log history
@router.get("/history/{user_id}", response_model=list[MealLogOut])
def view_user_history(user_id: int, db: Session = Depends(get_db)):
    return mealTracking.get_user_history(db = db, user_id=user_id)


# Dynamic Path Parameter Endpoint: GET /meals/summary/{user_id}
# Note: You didn't define a 'response_model' here yet. By default, FastAPI will automatically 
# serialize your raw Python dictionary ('summary') into a valid JSON object string.
@router.get("/summary/{user_id}")
def read_summary(user_id: int, db: Session = Depends(get_db)):
    # Hand off the verified session and user_id directly to the computation engine above
    return mealTracking.get_summary(db = db, user_id=user_id)


@router.delete("/{user_id}/log/{meal_log_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_meal(user_id: int, meal_log_id: int, db: Session = Depends(get_db)):
    success = mealTracking.delete_meal(db, meal_log_id=meal_log_id, user_id=user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal log not found or does not belong to this user."
        )
    
    # HTTP 204 No Content successfully returns an empty body on a clean deletion
    return None