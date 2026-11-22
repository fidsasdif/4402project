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
first_names = [
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
last_names = [
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
cities = [
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
road_names = [
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

area_codes = ["225", "337", "504", "985"]


# ---------- helpers ----------
def make_ids(n):
    """The only place surrogate IDs are created: FIRST_ID, FIRST_ID+1, ..."""
    return list(range(FIRST_ID, FIRST_ID + n))


def random_phone():
    return f"{random.choice(area_codes)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_date(start, end):
    """A random date between start and end, inclusive."""
    return start + timedelta(days=random.randint(0, (end - start).days))


# ---------- rebuild the database from schema.sql ----------
conn = sqlite3.connect(DB_PATH)
conn.executescript(SCHEMA_PATH.read_text())
conn.execute("PRAGMA foreign_keys = ON")

