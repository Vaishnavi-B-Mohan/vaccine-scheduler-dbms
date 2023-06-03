CREATE TABLE Caregivers (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Patients (
    Username varchar(255),
    Salt BINARY(16),
    Hash BINARY(16),
    PRIMARY KEY (Username)
);

CREATE TABLE Availabilities (
    Time date,
    Username varchar(255) REFERENCES Caregivers,
    PRIMARY KEY (Time, Username)
);

CREATE TABLE Vaccines (
    Name varchar(255),
    Doses int,
    PRIMARY KEY (Name)
);

CREATE TABLE Appointments (
    AppointmentID UNIQUEIDENTIFIER default NEWID(),
    PatientID varchar(255) REFERENCES Patients,
    CaregiverID varchar(255) REFERENCES Caregivers,
    VaccineName varchar(255) REFERENCES Vaccines,
    Time date,
    PRIMARY KEY (AppointmentID)
);
