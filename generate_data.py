import sqlite3
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(1)

# ---------- configuration ----------
HERE = Path(__file__).parent
DB_PATH = HERE / "data.db"
SCHEMA_PATH = HERE / "schema.sql"
TODAY = date(2026, 11, 22)  # fixed "today" so every run produces identical data
FIRST_ID = 10001  # surrogate IDs start here so they're 5 digits

# ---------- word lists ----------
FIRST_NAMES = [
    "Kevin",
    "Jessica",
    "Adithya",
    "Kameron",
    "Pablo",
    "Evan",
    "Julian",
    "Joseph",
    "Francis",
    "Mason",
    "Aedan",
    "William",
    "Dwight",
    "Charles",
    "Oliver",
    "Owen",
    "Tyler",
    "Madison",
    "Alexandra",
    "Jasper",
    "Amiah",
    "Aalijah",
    "Mahmood",
    "Sammy",
    "Gabriel",
    "Caden",
    "Kiara",
    "Gavin",
    "Joy",
    "Phillip",
    "Abigail",
    "Emerson",
    "Scott",
]
LAST_NAMES = [
    "Underwood",
    "Sonnier",
    "Stanley",
    "Smith",
    "Otzenberger",
    "Parks",
    "Plessy",
    "Ricketts",
    "Russell",
    "Sinclair",
    "Nguyen",
    "Morris",
    "Morales",
    "Mendoza",
    "Mansour",
    "Lee",
    "Ledet",
    "Kirk",
    "King",
    "Jennings",
    "Jenkins",
    "Jasim",
    "Huong",
    "Hollier",
    "Hawk",
    "Guillory",
    "Green",
    "Faulk",
    "DeFrates",
    "Cunningham",
    "Couch",
    "Cazayoux",
    "Byrd",
    "Brown",
    "Broussard",
    "Antoine",
    "Albarran",
]
CITIES = [
    "Baton Rouge",
    "Lafayette",
    "Hammond",
    "Slidell",
    "Covington",
    "Mandeville",
    "Prairieville",
    "Gonzales",
    "St. Francisville",
    "New Orleans",
    "Houma",
]
ROAD_NAMES = [
    "Main St",
    "1st St",
    "2nd St",
    "3rd St",
    "4th St",
    "5th St",
    "Hwy 190",
    "Hwy 61",
    "Hwy 37",
    "Hwy 408",
    "Hwy 67",
    "Hwy 63",
    "Highland Rd",
    "Nicholson Rd",
    "Airline Blvd",
    "Florida Ave",
    "Jefferson St",
    "Sherwood St",
    "Burbank Dr",
    "Government Ave",
    "Perkins Rd",
    "Coursey Rd",
    "Siegen Ln",
    "Oak St",
    "Cedar Dr",
    "Maple Ln",
    "Pine St",
    "Elm Rd",
    "Willow Blvd",
    "Palm St",
    "Magnolia Ave",
    "Cypress St",
    "Sycamore Ln",
    "Birch St",
    "Ash Ave",
    "Cherry St",
    "Walnut Rd",
    "Hickory Ln",
    "Poplar St",
    "Spruce Dr",
    "Fir St",
    "Redwood Ave",
    "Sequoia Rd",
    "Juniper Ln",
    "Larch St",
    "Alder Ave",
    "Beech Rd",
    "Chestnut Ln",
]
AREA_CODES = ["225", "337", "504", "985"]
SHELTER_ADJECTIVES = [
    "Friendsip",
    "Sunshine",
    "Happy Place",
    "Furrever",
    "Lucky Paws",
    "New Leash",
    "Paws & Claws",
    "Fountain of Hope",
    "Golden Heart",
    "Bright Futures",
    "Riverbend",
    "Magnolia",
    "Cypress Grove",
    "Live Oak",
    "Gulf CoastLagniappe",
]
SHELTER_NOUNS = [
    "Adoption Center",
    "Animal Shelter",
    "Pet Rescue",
    "Animal Rescue",
    "Vet and Adoption",
    "Animal Sanctuary",
    "Pet Haven",
    "Animal Care Center",
]


# ---------- helpers ----------
def make_ids(n):
    """The only place surrogate IDs are created: FIRST_ID, FIRST_ID+1, ..."""
    return list(range(FIRST_ID, FIRST_ID + n))


def random_phone():
    return f"{random.choice(AREA_CODES)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_date(start, end):
    """A random date between start and end, inclusive."""
    return start + timedelta(days=random.randint(0, (end - start).days))


# ---------- rebuild the database from schema.sql ----------
conn = sqlite3.connect(DB_PATH)
conn.executescript(SCHEMA_PATH.read_text())
conn.execute("PRAGMA foreign_keys = ON")

# ---------- shelter ----------
shelter_ids = make_ids(36)
shelter_cities = random.sample(CITIES, len(shelter_ids))
shelter_adjectives = random.sample(SHELTER_ADJECTIVES, len(shelter_ids))
shelters = []

for id, city, adjective in zip(shelter_ids, shelter_cities, shelter_adjectives):
    name = f"{adjective} {random.choice(SHELTER_NOUNS)}"
    shelters.append(
        (
            id,
            name,
            f"{random.randint(1000, 9999)} {random.choice(ROAD_NAMES)}",
            city,
            "LA",
            random_phone(),
            random.randint(15, 150),
        )
    )

conn.executemany(
    "INSERT INTO Shelter (ID, Name, Address, City, State, PhoneNumber, Capacity) VALUES (?, ?, ?, ?, ?, ?, ?)", shelters
)

conn.commit()
conn.close()
print("\nShelters: {len(shelters)}\n")
