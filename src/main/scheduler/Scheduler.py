from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Appointments import Appointments
from model.Availabilities import check_availability
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import re


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None

login_profile_name = None


def create_patient(tokens):
    print("Password should contain atleast 8 characters, both cases, letters and numbers, and atleast one special character from ! @ # ?")
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return

    # check 3: Password handling for strong passwords
    ret_code = password_handling(password)
    if ret_code == 1:
        print("Failed to create user. Password length has to be atleast 8 characters")
        return
    elif ret_code == 2:
        print("Failed to create user. Password has to contain both upper and lower cases")
        return
    elif ret_code == 3:
        print("Failed to create user. Password has to contain both letters and numbers")
        return
    elif ret_code == 4:
        print("Failed to create user. Password has to contain atleast one special character from ! @ # ?")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    print("Password should contain atleast 8 characters, both cases, letters and numbers, and atleast one special character from ! @ # ?")

    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    # check 3: Password handling for strong passwords
    ret_code = password_handling(password)
    if ret_code == 1:
        print("Failed to create user. Password length has to be atleast 8 characters")
        return
    elif ret_code == 2:
        print("Failed to create user. Password has to contain both upper and lower cases")
        return
    elif ret_code == 3:
        print("Failed to create user. Password has to contain both letters and numbers")
        return
    elif ret_code == 4:
        print("Failed to create user. Password has to contain atleast one special character from ! @ # ?")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def password_handling(password):
    # fail conditions:
    # 1: Password length is less than 8 characters
    # 2: Password does not contain both cases
    # 3: Password does not contain a mixture of letters and numbers
    # 4: Password does not contain any special character

    regex = re.compile('[!@#?]')
    if len(password) < 8:
        print("Password must have atleast 8 characters. Please try again!")
        return 1
    if password.isupper() or password.islower():
        return 2
    if password.isalpha() or password.isnumeric():
        return 3
    if regex.search(password) is None:
        return 4
    else:
        return 0

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    global login_profile_name
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
        login_profile_name = username
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    global login_profile_name
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
        login_profile_name = username
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    #  search_caregiver_schedule <date>
    #  check 1: check if a user is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Input length is incorrect. Please try again!")
        return
    date = tokens[1]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    try:
        d = datetime.datetime(year, month, day)
        row_count = check_availability(d)
        if row_count == 0:
            print("Sorry! No caregiver/vaccine available for this date. Please choose a different date.")
    except pymssql.Error as e:
        print("Search_caregivers_schedule Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date in MM-DD-YYYY format!")
    except Exception as e:
        print("Error occurred when searching for caregiver schedules. Please try again!")
        print("Error:", e)
    return


def reserve(tokens):
    #  reserve <date> <vaccine>
    #  check 1: check if a patient is logged in
    global current_patient
    global login_profile_name
    if current_caregiver is not None:
        print("Please login as a patient!")
        return
    if current_patient is None and current_caregiver is None:
        print("Please login first!")
        return
    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Input length is incorrect. Please try again!")
        return

    date = tokens[1]
    vaccinename = tokens[2]
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])

    try:
        d = datetime.datetime(year, month, day)
        patient_name = login_profile_name
        appointment = Appointments().create_appointment(patient_name, vaccinename, d)
        if len(appointment) != 0:
            print("Your appointment has been reserved successfully!")
            print("Appointment ID: ", appointment[0], "Caregiver username: ", appointment[1])

    except pymssql.Error as e:
        print("Error occurred when reserving an appointment! Please try again")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("And error occured while reserving an appointment!")
    except Exception as e:
        print("Error occurred when reserving an appointment. Please try again!")
        print("Error:", e)

    return


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        ret_code = current_caregiver.upload_availability(d)
        if ret_code == 1:
            print("Availability uploaded!")
        else:
            print("Upload Availability Failed")
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date in MM-DD-YYYY format!")
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
    finally:
        return


def cancel(tokens):
    #  check 1: check if a user is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Input length is incorrect. Please try again!")
        return

    try:
        appointmentID = tokens[1]
        ret_code = Appointments().cancel_appointment(appointmentID)
        if ret_code == 1:
            print("Your appointment has been canceled!")
        else:
            print("An error occured in canceling the appointment. Please try again")

    except Exception as e:
        print("An error occured in canceling the appointment. Please try again")
        print("Error:", e)
    return

def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    global login_profile_name
    #  check 1: check if a user is logged in
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return

    try:
        if current_caregiver is not None:
            Appointments().see_cg_appointments(login_profile_name)
        elif current_patient is not None:
            Appointments().see_patient_appointments(login_profile_name)

    except pymssql.Error as e:
        print("Failed to show appointments!")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Error! Please try again")
    except Exception as e:
        print("Error occurred when showing appointments. Please try again!")
        print("Error:", e)
    return


def logout(tokens):
    global current_caregiver
    global current_patient
    global login_profile_name
    if current_caregiver is None and current_patient is None:
        print("Please login first!")
        return
    try:
        current_patient = None
        current_caregiver = None
        login_profile_name = None
        print("Successfully logged out!")
        return None

    except Exception as e:
        print("Logout failed! Please try again")
        print("Error:", e)
        return None



def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # //
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # //
    print("> reserve <date> <vaccine>")  # //
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # //
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # //
    print("> logout")  # //
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        #response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        operation = operation.lower()
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
