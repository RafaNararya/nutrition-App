from sqlalchemy import Integer, Float, String, Column
from app.utils.db import Base

class Food(Base):
    __tablename__ = "usda_foods"

    fdc_id = Column(Integer, primary_key = True, index = True)
    description = Column(String)
    Protein = Column(Float)
    Fats = Column(Float)
    Carbs = Column(Float)
    Calories = Column(Float)