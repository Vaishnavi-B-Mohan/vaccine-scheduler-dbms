import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql


class Caregiver:
    def __init__(self, username, password=None, salt=None, hash=None):
        self.username = username
        self.password = password
        self.salt = salt
        self.hash = hash

    # getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)

        get_caregiver_details = "SELECT Salt, Hash FROM Caregivers WHERE Username = %s"
        try:
            cursor.execute(get_caregiver_details, self.username)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self.password, curr_salt)
                if not curr_hash == calculated_hash:
                    # print("Incorrect password")
                    cm.close_connection()
                    return None
                else:
                    self.salt = curr_salt
                    self.hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    def get_username(self):
        return self.username

    def get_salt(self):
        return self.salt

    def get_hash(self):
        return self.hash

    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_caregivers = "INSERT INTO Caregivers VALUES (%s, %s, %s)"
        try:
            cursor.execute(add_caregivers, (self.username, self.salt, self.hash))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()

    # Insert availability with parameter date d
    def upload_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        chk_exist_appointment = "SELECT AppointmentID FROM Appointments WHERE CaregiverID = %s AND Time = %s"
        chk_existing_availability = "SELECT COUNT(Time) FROM Availabilities WHERE Username = %s AND Time = %s"
        add_availability = "INSERT INTO Availabilities VALUES (%s , %s)"
        try:
            # check 1: Check if there is an existing appointment on that date. If so, suggest the user to cancel the appointment before uploading availability
            cursor.execute(chk_exist_appointment, (self.username, d))
            for row in cursor:
                existing_appointment = row[0]
                if existing_appointment is not None:
                    print("There is an active appointment already booked at this time. Please cancel this and try again. AppointmentID: ", row[0])
                    return
            # check 2: Check if the availability already exists for the user in the availability table. If so, notify the user about it already existing
            cursor.execute(chk_existing_availability, (self.username, d))
            for row in cursor:
                existing_availability = row[0]
                if existing_availability != 0:
                    print("Availability has already been added for this date.")
                    return

            # add availability to the database
            cursor.execute(add_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
            print("Availability uploaded!")
        except pymssql.Error:
            # print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()
            return

    def remove_availability(self, d):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        del_availability = "DELETE FROM Availabilities WHERE Time=%s AND Username=%s"
        try:
            cursor.execute(del_availability, (d, self.username))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when updating caregiver availability")
            raise
        finally:
            cm.close_connection()
