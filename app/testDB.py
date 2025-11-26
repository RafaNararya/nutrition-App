from db import engine

try:
    conn = engine.connect()
    print("Connection Successful")
    conn.close()
except Exception as e:
    print("Connection Failed", e)
