from sqlalchemy.orm import Session
from app.models.food import Food

def search_food_items(db: Session, query: str):
    to_search = f"%{query}%"
    return db.query(Food).filter(Food.description.ilike(to_search)).all()

