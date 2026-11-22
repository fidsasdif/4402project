import sqlite3
import random
random.seed(1)

with sqlite3.connect("data.db") as conn:        
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

first_names = ["Kevin", "Jessica", "Adithya", "Kameron", "Pablo", "Evan", "Julian", "Joseph", "Francis", "Mason", "Aedan", "William", "Dwight", "Charles", "Oliver", "Owen", "Tyler", "Madison", "Alexandra", "Jasper", "Amiah", "Aalijah", "Mahmood", "Sammy", "Gabriel", "Caden", "Kiara", "Gavin", "Joy", "Phillip", "Abigail", "Emerson", "Scott"]
last_names = ["Underwood", "Sonnier", "Stanley", "Smith", "Otzenberger", "Parks", "Plessy", "Ricketts", "Russell", "Sinclair", "Nguyen", "Morris", "Morales", "Mendoza", "Mansour", "Lee", "Ledet", "Kirk", "King", "Jennings", "Jenkins", "Jasim", "Huong", "Hollier", "Hawk", "Guillory", "Green", "Faulk", "DeFrates", "Cunningham", "Couch", "Cazayoux", "Byrd", "Brown", "Broussard", "Antoine", "Albarran"]
pet_names = ["Edward Pillbottle", "Abu Bakr al-Baghdadi"]
cities = ["Baton Rouge", "Lafayette", "Hammond", "Slidell", "Covington", "Mandeville", "Prarieville", "Gonzales", "St. Francisville", "New Orleans", "Houma"]
road_names = ["Main St", "1st St", "2nd St", "3rd St", "4th St", "5th St", "Hwy 190", "Hwy 61", "Hwy 37", "Hwy 408", "Hwy 67", "Hwy 63", "Highland St", "Nicholson Rd", "Airline Blvd", "Florida Ave", "Jefferson St", "Sherwood St", "Burbank Rd", "Government Ave", "Perkins St", "Coursey Rd", "Siegan St", "Oak St", "Cedar Dr", "Maple Ln", "Pine St", "Elm Rd", "Willow Blvd", "Palm St", "Magnolia Ave", "Cypress St", "Sycamore Ln", "Birch St", "Ash Ave", "Cherry St", "Walnut Rd", "Hickory Ln", "Poplar St", "Spruce Dr", "Fir St", "Redwood Ave", "Sequoia Rd", "Juniper Ln", "Larch St", "Alder Ave", "Beech Rd", "Chestnut Ln"]
animal_breed = {"Dog": ["Mixed", "Golden Retriever", "German Shepherd", "Bulldog", "Beagle", "Labrador", "Dachshund", "Yorkshire Terrier", "Rottweiler", "Husky", "Chihuahua", "Great Dane", "Cocker Spaniel", "Border Collie"]}
area_codes = ["225", "337", "504", "985"]

shelters = [
    (i, f"Shelter {i}", f"{random.randint(1000, 9999)} {random.choice(road_names)}", random.choice(cities), "LA", 
     f"{random.choice(area_codes)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}", random.randint(10, 35)) 
     for i in range(1, 11)
]
cursor.executemany("INSERT INTO Shelter (ID, Name, Address, City, State, PhoneNumber, Capacity) VALUES (?, ?, ?, ?, ?, ?, ?);", shelters)

shelter_capacities = {s[0]: s[6] for s in shelters}

pets = []
for i in range(1, 251):
    animal = random.choice(list(animal_breed.keys()))
    status = random.choice(["Available", "Pending", "Adopted"])

    open_shelters = [s_id for s_id, capacity in shelter_capacities.items() if capacity > 0]
    shelter_id = random.choice(open_shelters)
    if status != "Adopted":
        shelter_capacities[shelter_id] -= 1

    pets.append((i, shelter_id, random.choice(pet_names), animal, random.choice(animal_breed[animal]), 
                 f"{random.randint(2015, 2024)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}", random.choice(["Male", "Female"]), 
                 status, f"{random.randint(2025, 2026)}-{random.randint(1, 11):02d}-{random.randint(1, 28):02d}"
            )) 
cursor.executemany("INSERT INTO Pet (ID, Shelter_ID, Name, Species, Breed, BirthDate, Sex, AdoptionStatus, DateTakenIn) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", pets)

adopters = []
for i in range(1, 201):
    firstname = random.choice(first_names)
    lastname = random.choice(last_names)
    adopters.append((f"{firstname.lower()}{lastname.lower()}{random.randint(1, 100)}@{random.choice(['gmail', 'yahoo', 'hotmail'])}.com", firstname, lastname,
     f"{random.randint(100, 999)} {random.choice(road_names)}", f"{random.choice(area_codes)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
                ))
cursor.executemany(
    "INSERT INTO Adopter (Email, FirstName, LastName, Address, PhoneNumber) VALUES (?, ?, ?, ?, ?)", adopters)

conn.commit()
conn.close()