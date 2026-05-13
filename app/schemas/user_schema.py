from pydantic import BaseModel, EmailStr
#BaseModel. By inheriting this, you create classes that automatically handle data validation
#When you create an instance of a model, Pydantic ensures the input data matches the defined types you have, or else it raises a validationerror
#BaseModel also automatically attempts to "fit" sent in data to the data types that was defined 
#Basically very good for data handling security. Doing this stuff manually would be a pain

#Input Blueprint ensuring that when someone signs up, they MUST enter a String Username and an Email
class UserCreate(BaseModel):
    username: str
    email: EmailStr #EmailStr from pydantic makes it so it ensures users type in an "@" and a "."

#Output Blueprint 
class UserOut(BaseModel):
    id: int 
    username: str
    email: EmailStr

    class Config: 
        from_attributes = True
        #Without these lines of code, Pydantic expects data to be in a dictionary format. Databases usually store
        #data in instance attributes, so this line tells Pydantic to look for those values when validating an object
        #This basically allows it so that Pydantic can read it arbitrary objects instead of just dictionary formatted data