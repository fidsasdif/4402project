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
NUM_SHELTERS = 36
MIN_CAPACITY, MAX_CAPACITY = 15, 50
MAX_STEM_USES = 2  # a stem can appear on at most this many shelters
STEM_REUSE_CHANCE = 0.2  # chance a shelter reuses a stem another city already has

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
# city -> (size weight, area code). The weight (roughly population) drives both
# how many shelters a city gets and how big those shelters are
CITY_INFO = {
    # big
    "New Orleans": (8, "504"),
    "Baton Rouge": (8, "225"),
    "Shreveport": (6, "318"),
    "Lafayette": (5, "337"),
    # medium
    "Metarie": (4, "504"),
    "Lake Charles": (3, "337"),
    "Kenner": (2, "504"),
    "Bossier City": (2, "318"),
    "Monroe": (2, "318"),
    "Alexandria": (2, "318"),
    "Houma": (2, "985"),
    "Slidell": (2, "985"),
    # small
    "Hammond": (1, "985"),
    "Covington": (1, "985"),
    "Mandeville": (1, "985"),
    "Prairieville": (1, "225"),
    "Gonzales": (1, "225"),
    "St. Francesville": (1, "225"),
    "New Iberia": (1, "337"),
    "Ruston": (1, "318"),
    "Natchitoches": (1, "318"),
    "Thibodaux": (1, "985"),
}
CITIES = list(CITY_INFO)

CITY_WEIGHTS = [weight for weight, _ in CITY_INFO.values()]

SHELTER_ADJECTIVES = [
    "Friendship",
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
    "Gulf Coast",
    "Lagniappe",
    "Purrfect Match",
    "Whiskers & Wags",
    "Nine Lives",
    "Cuddle Corner",
    "Feathers & Fur",
    "Hop Along",
    "Welcome Home",
    "Firefly",
    "Azalea",
    "Honeysuckle",
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


def random_phone(city):
    """A phone number with an area code for that city."""
    area_code = CITY_INFO[city][1]
    return f"{area_code}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"


def random_date(start, end):
    """A random date between start and end, inclusive."""
    return start + timedelta(days=random.randint(0, (end - start).days))


# ---------- rebuild the database from schema.sql ----------
conn = sqlite3.connect(DB_PATH)
conn.executescript(SCHEMA_PATH.read_text())
conn.execute("PRAGMA foreign_keys = ON")

# ---------- shelter ----------
shelter_ids = make_ids(NUM_SHELTERS)

# pick cities first because a shelter's name depends on which stems its city already has
shelter_cities = random.choices(CITIES, weights=CITY_WEIGHTS, k=NUM_SHELTERS)

stem_uses = {stem: 0 for stem in SHELTER_ADJECTIVES}  # how many shelters use each stem
stems_in_city = {city: set() for city in CITIES}  # stems already used in each city
used_names = set()  # full names already taken

shelters = []
for s_id, city in zip(shelter_ids, shelter_cities):
    # stems this shelter may use: not used up, and not already used in this city
    allowed = [s for s in SHELTER_ADJECTIVES if stem_uses[s] < MAX_STEM_USES and s not in stems_in_city[city]]
    if not allowed:
        raise ValueError(f"No stems left for a shelter in {city}: add more SHELTER ADJECTIVES")
    fresh = [s for s in allowed if stem_uses[s] == 0]  # nobody has this stem yet
    reused = [s for s in allowed if stem_uses[s] > 0]  # another city has this stem

    if reused and (not fresh or random.random() < STEM_REUSE_CHANCE):
        stem = random.choice(reused)
    else:
        stem = random.choice(fresh)

    # pick an ending that doesn't recreate an existing full name
    endings = [n for n in SHELTER_NOUNS if f"{stem} {n}" not in used_names]
    name = f"{stem} {random.choice(endings)}"

    stem_uses[stem] += 1
    stems_in_city[city].add(stem)
    used_names.add(name)

    # bigger city -> bigger shelter (weight 1 ~ 19, weight 8 ~ 47), clamped to 15-50
    weight = CITY_INFO[city][0]
    capacity = max(MIN_CAPACITY, min(MAX_CAPACITY, 15 + 4 * weight + random.randint(-5, 5)))
    shelters.append(
        (
            s_id,
            name,
            f"{random.randint(1000, 9999)} {random.choice(ROAD_NAMES)}",
            city,
            "LA",
            random_phone(city),
            capacity,
        )
    )

conn.executemany(
    "INSERT INTO Shelter (ID, Name, Address, City, State, PhoneNumber, Capacity) VALUES (?, ?, ?, ?, ?, ?, ?)", shelters
)

# expected intake follows capacity (bigger shelters take in more animals); the random "busy-ness" factor decides which
# shelters end up overcrowded. Not stored in the database: the Pet section uses it to choose intake shelters.
shelter_intake_weights = [s[6] * random.lognormvariate(0, 0.5) for s in shelters]

conn.commit()
conn.close()

print(f"\nShelters: {len(shelters)}\n")
