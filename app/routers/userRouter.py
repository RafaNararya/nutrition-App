from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.schemas.user_schema import UserCreate, UserOut, userProfileUpdate
from app.services import userServices

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
    return userServices.create_user(db = db, user = user)

@router.put("/profile/{user_id}", response_model=UserOut)
def update_profile(user_id: int, profile: userProfileUpdate, db: Session = Depends(get_db)):
    updated_user = userServices.updateUser(db = db, user_id = user_id, profile_info = profile)

    if not updated_user: 
        raise HTTPException(status_code = 404, detail = "User not Found")
    
    return updated_user