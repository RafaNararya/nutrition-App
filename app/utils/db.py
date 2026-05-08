import os
from sqlalchemy import create_engine
#"engine" is a object that allows talking to Postgres. It manages a "connection pool"
#A set of connections so that a new connection doesn't have to restart everytime i need it

from sqlalchemy.ext.declarative import declarative_base
#declarative_base returns a class "Base". When it comes to tables, this is the format that you want to inherit
#All database models that want to be tracked by the ORM (Object Relational Mapping) must follow the class Base
#ORM makes it so python (or any other language) can indirectly speak SQL through python/whatever code rather than raw SQL

from sqlalchemy.orm import sessionmaker
#Creates a "Session factory". A "session" is a single transaction/conversation with the database

from dotenv import load_dotenv
#loads like all the variables from .env so that it can be used in here

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
#make an engine/"connection pool" called engine. must do to have sessions with database

sessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
#creates a thing that can pump out individual sessions/conversations with database
#autocommit = False tells SQLAlchemy not to send data to the DB until it is told to
#autoflush = False prevents SQLAlchemy from sending "test" queries to the DB before ready
#bind = engine !!!!Is the key!!!! links the conversation generations to the specific postgres engine "connection pool"

Base = declarative_base()

def get_db():
    db = sessionLocal()
    # instantiates one specific "conversation"
    try:
        yield db
        #gives the connection to the FastAPI Route. It pauses here while the route runs
    finally:
        db.close()
        #once the route is finished, no matter what, the connection is closed
        #IMPORTANT to not crash the DB