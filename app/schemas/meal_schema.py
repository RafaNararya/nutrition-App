from pydantic import BaseModel
from datetime import datetime
from typing import Optional

#Creation of a meal blueprint
#It requires to be passed in a UserId, foodId, and the amount of food in grams
#The only thing the user will have to worry about is typing the type of food (user design issue) and the amount planned for it
#Eventually, the server will send a "token" to every specific user when they log in, and it'll automatically be injected for every userId
#field that is used. 
class MealLogCreate(BaseModel):
    user_id: int
    food_id: int
    quantity_grams: float = 100.0 #Kind of a precautionary to prevent crashes if they dont enter anything 

class MealLogOut(BaseModel):
    id: int
    user_id: int
    food_id: int
    quantity_grams: float
    created_at: datetime #This is so that Postgres can create a timestamp, so that we can print it out for the user to see
    # Something like "Logged at 12:30 pm EST" or something

    class Config:
        from_attributes = True
        #Without these lines of code, Pydantic expects data to be in a dictionary format. Databases usually store
        #data in instance attributes, so this line tells Pydantic to look for those values when validating an object
        #This basically allows it so that Pydantic can read it arbitrary objects instead of just dictionary formatted data