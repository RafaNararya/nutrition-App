#Connection to FastAPI. FastAPI starter

from fastapi import FastAPI
from app.routers import testRouter, userRouter, mealRouter, recommendationRouter
from app.models import food, meal, user
from app.utils.db import Base, engine, sessionLocal
from contextlib import asynccontextmanager
from app.services.recommendationEngine import initialize_recommendation_engine
from fastapi.middleware.cors import CORSMiddleware

# an 'asynccontextmanager' controls startup and shutdown events
# Anything written BEFORE the "yield" statement happens when the app wakes up
# Anything written AFTER the "yield" would happen when the server is shut down
@asynccontextmanager
async def lifespan(app: FastAPI):

    # creates a temporary session to the database
    db = sessionLocal()
    try:
        # Fire off our engine initialization function
        # This loads the dataframes and builds the model into memory right as the server starts up
        initialize_recommendation_engine(db)
        print(f"Recommendation Engine Initialized")
    except Exception as e:
        print(f"Failed to initialize recommendation engine: {e}")
    finally:
        db.close()
    
    yield # This is where the server is actually ready to start running and handle requests



app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)




app.include_router(testRouter.router)
#.include_router("routerFileName".router): should be done for every new router file

app.include_router(userRouter.router)
app.include_router(mealRouter.router)
app.include_router(recommendationRouter.router)


Base.metadata.create_all(bind=engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to Rafa's Nutrition App"}

@app.get("/status")
def check_status():
    return {"Status": "Database is live", "Rows": 376}