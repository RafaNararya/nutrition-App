from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate, userProfileUpdate

"""def create_user(db: Session, user: UserCreate):
    #Take the UserCreate (Which Holds JSON Data) and turn it into a User Object
    #Just a reminder that the User object in app/models takes in an ID, Username, and Email
    #This needs to be done so it can be added into the actual Database (Postgres) or else nothing can be read in by Postgres
    new_user = User(username = user.username, email = user.email)

    #Kind of like Git, the first line prepares Postgres to receive the new_user object
    #Commit finishes the deal and actually adds it into the database
    db.add(new_user)
    db.commit()

    #You notice that when we created new_user, we never passed in an id. Thats because the user is not supposed to be the one that passes in the ID
    #It's going to be automatically done by Postgres. it should be done like this.
    #Hitting refresh on the DB basically forces Postgres to auto-assign the "non-IDed object" with an ID
    db.refresh(new_user)
    return new_user"""

def updateUser(db: Session, user_id: int, profile_info: userProfileUpdate):
    # Look for the user in the database
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        return None

    # Helper to convert Enum to raw string if necessary
    activity_val = profile_info.activity_level.value if hasattr(profile_info.activity_level, 'value') else profile_info.activity_level

    # Overwrite previous biometric attributes
    db_user.age = profile_info.age
    db_user.gender = profile_info.gender
    db_user.weight_kg = profile_info.weight_kg
    db_user.height_cm = profile_info.height_cm
    db_user.activity_level = activity_val

    db.commit()
    db.refresh(db_user)

    # Convert object to dict to guarantee activity_level is a plain string in the JSON payload
    user_dict = {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "age": db_user.age,
        "gender": db_user.gender,
        "weight_kg": db_user.weight_kg,
        "height_cm": db_user.height_cm,
        "activity_level": str(db_user.activity_level.value if hasattr(db_user.activity_level, 'value') else db_user.activity_level)
    }

    return user_dict