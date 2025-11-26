#Managaes and executes database connections and SQL Queries

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os
import psycopg2


def test_query():
    load_dotenv()
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

    conn.autocommit = True
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    result = cursor.fetchall()
    cursor.close()
    conn.close()

    return result













# DATABASE_URL = f"postgresql://{DB_USER}: {DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

'''engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()'''
