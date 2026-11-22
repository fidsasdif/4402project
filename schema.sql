PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS Transfer;
DROP TABLE IF EXISTS MedicalRecords;
DROP TABLE IF EXISTS Adoption;
DROP TABLE IF EXISTS Application;
DROP TABLE IF EXISTS Staff;
DROP TABLE IF EXISTS Pet;
DROP TABLE IF EXISTS Adopter;
DROP TABLE IF EXISTS Shelter;

PRAGMA foreign_keys = ON;

CREATE TABLE Shelter (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL,
    Address TEXT NOT NULL,
    City TEXT NOT NULL,
    State TEXT NOT NULL,
    PhoneNumber TEXT,
    Capacity INTEGER
);

CREATE TABLE Pet (
    ID INTEGER PRIMARY KEY,
    Shelter_ID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Species TEXT NOT NULL,
    Breed TEXT,
    BirthDate DATE,
    Sex TEXT,
    AdoptionStatus TEXT NOT NULL,
    DateTakenIn DATE NOT NULL,
    FOREIGN KEY (Shelter_ID) REFERENCES Shelter(ID)
);

CREATE TABLE Adopter (
    Email TEXT PRIMARY KEY,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Address TEXT NOT NULL,
    PhoneNumber TEXT
);

CREATE TABLE Application (
    ID INTEGER PRIMARY KEY,
    Pet_ID INTEGER NOT NULL,
    Adopter_Email TEXT NOT NULL,
    Shelter_ID INTEGER NOT NULL,
    Status TEXT NOT NULL,
    Date DATE NOT NULL,
    FOREIGN KEY (Pet_ID) REFERENCES Pet(ID),
    FOREIGN KEY (Adopter_Email) REFERENCES Adopter(Email),
    FOREIGN KEY (Shelter_ID) REFERENCES Shelter(ID)
);

CREATE TABLE Adoption (
    Application_ID INTEGER PRIMARY KEY,
    Pet_ID INTEGER NOT NULL,
    Adopter_Email TEXT NOT NULL,
    Shelter_ID INTEGER NOT NULL,
    Status TEXT NOT NULL,
    Date DATE NOT NULL,
    FOREIGN KEY (Application_ID) REFERENCES Application(ID),
    FOREIGN KEY (Pet_ID) REFERENCES Pet(ID),
    FOREIGN KEY (Adopter_Email) REFERENCES Adopter(Email),
    FOREIGN KEY (Shelter_ID) REFERENCES Shelter(ID)
);

CREATE TABLE MedicalRecords (
    Pet_ID INTEGER NOT NULL,
    Date DATE NOT NULL,
    Time TIME NOT NULL,
    VaccinationStatus TEXT NOT NULL,
    Notes TEXT,
    Treatments TEXT,
    Vet_ID INTEGER NOT NULL,
    PRIMARY KEY (Pet_ID, Date, Time),
    FOREIGN KEY (Pet_ID) REFERENCES Pet(ID),
    FOREIGN KEY (Vet_ID) REFERENCES Staff(ID)
);

CREATE TABLE Staff (
    ID INTEGER PRIMARY KEY,
    Shelter_ID INTEGER NOT NULL,
    Name TEXT NOT NULL,
    Role TEXT NOT NULL,
    Email TEXT NOT NULL,
    PhoneNumber TEXT,
    FOREIGN KEY (Shelter_ID) REFERENCES Shelter(ID)
);

CREATE TABLE Transfer (
    Pet_ID INTEGER NOT NULL,
    From_Shelter_ID INTEGER NOT NULL,
    To_Shelter_ID INTEGER NOT NULL,
    Date DATE NOT NULL,
    Reason TEXT,
    PRIMARY KEY (Pet_ID, From_Shelter_ID, To_Shelter_ID),
    FOREIGN KEY (Pet_ID) REFERENCES Pet(ID),
    FOREIGN KEY (From_Shelter_ID) REFERENCES Shelter(ID),
    FOREIGN KEY (To_Shelter_ID) REFERENCES Shelter(ID)
);
