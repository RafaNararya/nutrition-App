from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.schemas.user_schema import UserCreate, UserOut, userProfileUpdate, UserLogin
from app.services import userServices
from app.services import userService

#Prefix /users means all routes here start with http://localhost:8000/users
#tags= makes it so that routes are easily findable in SwaggerUI (localhost/docs)
#Good for scalability later on when needing to do the frontend and just overall checking
router = APIRouter(prefix="/users", tags=["Users"])

#response_model= is basically what is used to filter information
#Whatever the database comes back with, this router will only output whatever UserOut was MEANT to output
#Basically just gives the stuff we want without all the noise
@router.post("/", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Depends(get_db): This is "Dependency Injection." 
    # It opens a database connection before the function starts and closes it when it's done. 
    # This prevents your app from leaking memory or crashing Postgres with too many idle connections.
    return userService.create_user(db = db, user = user)

# .put() keyword is equivalent to a theme of "updating" already established information
# kinda like when an initial profile is created, that will use a .post()
# but when you put in more specific information after the profile was created, that stuff will use a .put()
@router.put("/profile/{user_id}", response_model=UserOut)
def update_profile(user_id: int, profile: userProfileUpdate, db: Session = Depends(get_db)):
    # Call the service function to update the database row
    updated_user = userServices.updateUser(db = db, user_id = user_id, profile_info = profile)

    # Safeguard in case the service returns nothing, which means that the user that was intended to update does not exist in my database
    if not updated_user: 
        raise HTTPException(status_code = 404, detail = "User not Found")
    
    return updated_user


@router.post("/login", response_model=UserOut)
def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    return userService.authenticate_user(db, login_data)