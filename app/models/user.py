from sqlalchemy import Column, Integer, String, Enum, Float
import enum
from app.utils.db import Base

class ActivityLevel(str, enum.Enum):
    SEDENTARY = "sedentary"
    LIGHT = "lightly_active"
    MODERATE = "moderately_active"
    ACTIVE = "very_active"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique = True, index = True)
    email = Column(String, unique = True, index = True)
    #add height/weight/goals later

    # new biometrics for personalized recommended values
    age = Column(Integer, nullable = True)
    gender = Column(String, nullable = True)
    weight_kg = Column(Float, nullable = True)
    height_cm = Column(Float, nullable = True)
    activity_level = Column(Enum(ActivityLevel), default = ActivityLevel.SEDENTARY)