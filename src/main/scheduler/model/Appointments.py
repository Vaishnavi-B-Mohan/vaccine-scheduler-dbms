import sys
import uuid

sys.path.append("../db/*")
sys.path.append("../model/*")
from model.Caregiver import Caregiver
from model.Vaccine import Vaccine
from model.Availabilities import check_availability
from model.Availabilities import get_available_caregiver
from db.ConnectionManager import ConnectionManager
import pymssql


# Creating a unique ID (GUID) for every new appointment
def createAppointmentID():
    return str(uuid.uuid4())


class Appointments:
    def __init__(self):
        self.appointmentID = None
        self.patient = None
        self.caregiver = None
        self.vaccine = None
        self.d = None

    def get(self, appointmentID):
        self.appointmentID = appointmentID

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
                return self
        except pymssql.Error:
            # print("Error occurred when getting Appointment")
            raise
        finally:
            cm.close_connection()

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

    def create_appointment(self, patient, vaccine, d):
        self.appointmentID = str(uuid.uuid4())  # create a new GUID for every new appointment
        self.patient = patient
        self.vaccine = vaccine
        self.d = d
        try:
            availability = check_availability(self.d)
            if availability <= 0:
                print("Sorry no caregiver is available!")
                return None
            available_doses = Vaccine(self.vaccine).get_available_doses()
            if available_doses <= 0:
                print("Sorry not enough available doses!")
                return None

            self.caregiver = get_available_caregiver(self.d, self.vaccine)
            self.save_to_db()  # saving the appointment to the DB
            Vaccine(self.vaccine).decrease_available_doses(1)  # decreasing the available doses by 1 after reservation
            Caregiver(self.caregiver).remove_availability(d)  # remove caregiver availability from the Availabilities table after reservation

            return [self.appointmentID, self.caregiver]

        except Exception as e:
            print("Error occurred in reserving the appointment.")
            print("Error:", e)
            return None

    def cancel_appointment(self, appointmentID):
        self.appointmentID = appointmentID

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()
        try:
            find_appointment = "SELECT PatientID, CaregiverID, VaccineName, Time FROM Appointments WHERE AppointmentID = %s"
            cursor.execute(find_appointment, self.appointmentID)
            for row in cursor:
                if len(row) == 0:  # check if the appointment ID exists in the database
                    print("This appointmentID does not exist. Please try again!")
                    return 0

                self.patient = row[0]
                self.caregiver = row[1]
                self.vaccine = row[2]
                self.d = row[3]

            delete_appointment = "DELETE FROM Appointments WHERE AppointmentID = %s"
            cursor.execute(delete_appointment, self.appointmentID)
            conn.commit()

            Caregiver(self.caregiver).upload_availability(self.d)  # uploading availability for the caregiver after appointment cancellation
            Vaccine(self.vaccine).increase_available_doses(1)  # updating the number of available vaccine doses by one
            cm.close_connection()
            return 1

        except pymssql.Error:
            print("Error occurred in cancelling the appointment. Please try again")
            raise
        except Exception as e:
            print("Error occurred in cancelling the appointment. Please try again")
            print("Error:", e)
            return 0

    def see_cg_appointments(self, user):
        self.caregiver = user
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_appointments = "SELECT AppointmentID, VaccineName, Time, PatientID FROM Appointments WHERE CaregiverID = %s ORDER BY AppointmentID ASC"

        try:
            cursor.execute(get_appointments, self.caregiver)
            for row in cursor:
                self.appointmentID = row[0]
                self.vaccine = row[1]
                self.d = row[2]
                self.patient = row[3]
                print(self.appointmentID, self.vaccine, self.d, self.patient)

            return 1
        except pymssql.Error:
            print("Error occurred when getting Appointments")
            raise
        except Exception as e:
            print("Error occurred in cancelling the appointment. Please try again")
            print("Error:", e)
            return 0
        finally:
            cm.close_connection()

    def see_patient_appointments(self, user):
        self.patient = user
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_appointments = "SELECT AppointmentID, VaccineName, Time, CaregiverID FROM Appointments WHERE PatientID = %s"

        try:
            cursor.execute(get_appointments, self.patient)
            for row in cursor:
                self.appointmentID = row[0]
                self.vaccine = row[1]
                self.d = row[2]
                self.caregiver = row[3]
                print(self.appointmentID, self.vaccine, self.d, self.caregiver)
            return 1
        except pymssql.Error:
            print("Error occurred when getting Appointments")
            raise
        except Exception as e:
            print("Error occurred in cancelling the appointment. Please try again")
            print("Error:", e)
            return 0
        finally:
            cm.close_connection()
