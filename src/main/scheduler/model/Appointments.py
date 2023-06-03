import sys
import uuid
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql


def createAppointmentID():
    return str(uuid.uuid4())

class Appointments:
    def __init__(self, appointmentID, patient, caregiver, vaccine, d):
        self.appointmentID = appointmentID
        self.patient = patient
        self.caregiver = caregiver
        self.vaccine = vaccine
        self.d = d

    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_vaccine = "SELECT AppointmentID, PatientID, CaregiverID, VaccineName, Time FROM Appointments WHERE AppointmentID = %s"
        try:
            cursor.execute(get_vaccine, self.appointmentID)
            for row in cursor:
                self.patient = row['PatientID']
                self.caregiver = row['CaregiverID']
                self.vaccine = row['VaccineName']
                self.d = row['Time']
        except pymssql.Error:
            # print("Error occurred when getting Appointment")
            raise
            return
        finally:
            cm.close_connection()
            return self


    def get_appointmentID(self):
        return self.appointmentID


    def save_to_db(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_appointments = "INSERT INTO Appointments VALUES (%s, %s, %s, %s, %s)"
        try:
            # Check all data formats - TODO
            cursor.execute(add_appointments, (self.appointmentID, self.patient, self.caregiver, self.vaccine, self.d))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
            return

def see_cg_appointments(user):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    get_appointments = "SELECT AppointmentID, VaccineName, Time, PatientID FROM Appointments WHERE CaregiverID = %s ORDER BY AppointmentID ASC"

    try:
        cursor.execute(get_appointments, user)
        for row in cursor:
            appointmentID = row[0]
            vaccine_name = row[1]
            d = row[2]
            patient_name = row[3]
            print(appointmentID, vaccine_name, d, patient_name)

    except pymssql.Error:
        print("Error occurred when getting Appointments")
        raise
    finally:
        cm.close_connection()
        return None

def see_patient_appointments(user):
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    get_appointments = "SELECT AppointmentID, VaccineName, Time, CaregiverID FROM Appointments WHERE PatientID = %s"

    try:
        cursor.execute(get_appointments, user)
        for row in cursor:
            appointmentID = row[0]
            vaccine_name = row[1]
            d = row[2]
            caregiver_name = row[3]
            print(appointmentID, vaccine_name, d, caregiver_name)

    except pymssql.Error:
        print("Error occurred when getting Appointments")
        raise
    finally:
        cm.close_connection()
        return None
