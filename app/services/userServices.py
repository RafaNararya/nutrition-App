from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user_schema import UserCreate, userProfileUpdate

def create_user(db: Session, user: UserCreate):
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
    return new_user

def updateUser(db: Session, user_id: int, profile_info: userProfileUpdate):
    # Look for the first user in the database that has a match for the user_id
    db_user = db.query(User).filter(User.id == user_id).first()

    # If user doesn't exist, return a 404 Error
    if not db_user:
        return None

    # overwrite the previous biometric attributes with new, updated biometrics that follows the new schema data that is validated
    db_user.age = profile_info.age
    db_user.gender = profile_info.gender
    db_user.weight_kg = profile_info.weight_kg
    db_user.height_cm = profile_info.height_cm
    db_user.activity_level = profile_info.activity_level

    #Kind of like Git, the first line prepares Postgres to receive the db_user object
    #Commit finishes the deal and actually adds it into the database
    db.commit()
    db.refresh(db_user)

    return db_user