import sys

sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


# class Availabilities:
#     def __init__(self, d):
#         self.d = d

def check_availability(d):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    row_count = 0

    try:
        availability = "SELECT Username, Name, Doses FROM Availabilities, Vaccines WHERE Time = %s ORDER BY Username ASC"
        cursor.execute(availability, d)
        for row in cursor:
            cg_name = row[0]
            vaccine_name = row[1]
            vaccine_doses = row[2]
            if vaccine_doses > 0:
                print(cg_name, vaccine_name, vaccine_doses)
                row_count += 1
            else:
                print("Sorry! No vaccine available for this date")
        cm.close_connection()

    except pymssql.Error as e:
        raise e
    finally:
        cm.close_connection()
    return row_count

def get_available_caregiver(d, vaccine):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    cg_name = None
    try:
        availability = "SELECT TOP(1) A.Username FROM Availabilities AS A, Vaccines AS V WHERE A.Time = %s AND V.Name = %s AND V.Doses > 0 ORDER BY A.Username ASC"
        cursor.execute(availability, (d, vaccine))
        for row in cursor:
            cg_name = row[0]
        cm.close_connection()

    except pymssql.Error as e:
        raise e
    finally:
        cm.close_connection()
    return cg_name