from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MealLogCreate(BaseModel):
    user_id: int
    food_id: int
    quantity_grams: float = 100.0

class MealLogOut(BaseModel):
    id: int
    user_id: int
    food_id: int
    quantity_grams: float
    created_at: datetime

    class Config:
        from_attributes = True