from sqlalchemy.orm import Session
from app.models.food import Food

def search_food_items(db: Session, query: str):
    #db: Session; We want to take in an active session/conversation. Its how this function queries the database
    #query: str; its just whatever the user wants to look up i guess

    to_search = f"%{query}%"
    return db.query(Food).filter(Food.description.ilike(to_search)).all()
    #.query(): Takes in a table. its basically like SELECT * FROM (table name)
    #.description.ilike: is identical to "WHERE description ILIKE"
    #.all(): returns all of the results from the query, no limits
