from sqlalchemy import Integer, Float, String, Column
from app.utils.db import Base
#importing the structure of the database "Base"

class Food(Base):
    __tablename__ = "usda_foods"
    #Tells SQLAlchemy which table in Postgres to look at

    fdc_id = Column(Integer, primary_key = True, index = True)
    #Primary_key = True: tells that this is the unique ID for every row
    #index = True: Creates a map of this column so that searching by ID is O(1) (If Hashes are used)
    #In this, and every database case, Binary Trees are used, but look up times is still fast O(log(n))

    description = Column(String)
    Protein = Column(Float)
    Fats = Column(Float)
    Carbs = Column(Float)
    Calories = Column(Float)
    #Label each column and assign it its type of value