#This file performs logic and calls db.py functions.

from db import test_query

def test_Function():
    result = test_query()
    processed_result = {"db_status": result[0][0]}
    return processed_result