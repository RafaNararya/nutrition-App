#This will bridge the user and food files 
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.utils.db import Base

class mealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key = True, index = True)
    user_id = Column(Integer, ForeignKey("users.id"))
    food_id = Column(Integer, ForeignKey("usda_foods.fdc_id"))
    quantity_grams = Column(Float, default=100.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())