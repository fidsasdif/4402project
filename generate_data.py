import sqlite3
import random
import re
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
MIN_CAPACITY, MAX_CAPACITY = 8, 30
NUM_PETS = 800
MAX_STEM_USES = 2  # a stem can appear on at most this many shelters
STEM_REUSE_CHANCE = 0.2  # chance a shelter reuses a stem another city already has
NUM_ADOPTERS = 300
MAX_APPS_PER_ADOPTER = 3
HISTORICAL_TRANSFER_SHARE = 0.12  # of adopted pets that were transferred before adoption
DENIED_BEFORE_CHANCE = 0.2  # chance a Pending/Adopted pet also has an earlier Denied application
DENIED_AVAILABLE_CHANCE = 0.1  # chance an Available pet has one Denied application
SENIOR_AGE = 8  # pets this old (years) at adoption get half-price fees
ADOPTION_FEES = {"Dog": 150.0, "Cat": 100.0, "Rabbit": 50.0, "Bird": 40.0}
VISIT_COUNT_WEIGHTS = [40, 30, 20, 10]  # chance of 1, 2, 3 or 4 vet visits per pet

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
    "Emma",
    "Olivia",
    "Sophia",
    "Ava",
    "Isabella",
    "Mia",
    "Charlotte",
    "Amelia",
    "Harper",
    "Evelyn",
    "Ella",
    "Grace",
    "Chloe",
    "Lily",
    "Hannah",
    "Zoe",
    "Nora",
    "Riley",
    "Layla",
    "Brianna",
    "Destiny",
    "Jasmine",
    "Imani",
    "Aisha",
    "Fatima",
    "Priya",
    "Ananya",
    "Mei",
    "Linh",
    "Camila",
    "Valeria",
    "Lucia",
    "Ximena",
    "Maria",
    "Rosa",
    "Elena",
    "Claire",
    "Morgan",
    "Brooke",
    "Lauren",
    "Colette",
    "Amelie",
    "Liam",
    "Noah",
    "James",
    "Elijah",
    "Benjamin",
    "Lucas",
    "Henry",
    "Michael",
    "Daniel",
    "Matthew",
    "Sebastian",
    "Luke",
    "David",
    "Andrew",
    "Isaac",
    "Anthony",
    "Ethan",
    "Nathan",
    "Ryan",
    "Marcus",
    "Malik",
    "Jamal",
    "Andre",
    "Xavier",
    "Jalen",
    "Carlos",
    "Diego",
    "Mateo",
    "Omar",
    "Yusuf",
    "Arjun",
    "Minh",
    "Remy",
    "Beau",
    "Etienne",
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
    "Thibodeaux",
    "Landry",
    "Hebert",
    "Boudreaux",
    "Fontenot",
    "LeBlanc",
    "Breaux",
    "Arceneaux",
    "Robichaux",
    "Comeaux",
    "Doucet",
    "Guidry",
    "Savoie",
    "Trahan",
    "Melancon",
    "Theriot",
    "Prejean",
    "Bourgeois",
    "Babineaux",
    "Duhon",
    "Chauvin",
    "Gautreaux",
    "Naquin",
    "Dupre",
    "Mouton",
    "Batiste",
    "Johnson",
    "Williams",
    "Jones",
    "Davis",
    "Miller",
    "Wilson",
    "Anderson",
    "Thomas",
    "Harris",
    "Martin",
    "Thompson",
    "Robinson",
    "Clark",
    "Lewis",
    "Walker",
    "Hall",
    "Allen",
    "Young",
    "Wright",
    "Hill",
    "Adams",
    "Baker",
    "Nelson",
    "Carter",
    "Mitchell",
    "Turner",
    "Campbell",
    "Evans",
    "Washington",
    "Coleman",
    "Bryant",
    "Simmons",
    "Garcia",
    "Rodriguez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Ramirez",
    "Torres",
    "Rivera",
    "Castillo",
    "Tran",
    "Pham",
    "Patel",
    "Kim",
    "Chen",
    "Haddad",
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
    "Metairie": (4, "504"),
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
    "St. Francisville": (1, "225"),
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
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "lsu.edu"]

PET_NAMES = [
    "Bella",
    "Max",
    "Luna",
    "Charlie",
    "Daisy",
    "Cooper",
    "Lucy",
    "Bailey",
    "Sadie",
    "Rocky",
    "Molly",
    "Duke",
    "Zoe",
    "Bear",
    "Lola",
    "Tucker",
    "Stella",
    "Buddy",
    "Penny",
    "Bentley",
    "Rosie",
    "Gus",
    "Ruby",
    "Milo",
    "Nala",
    "Ollie",
    "Willow",
    "Leo",
    "Pepper",
    "Louie",
    "Coco",
    "Finn",
    "Hazel",
    "Murphy",
    "Ginger",
    "Bruno",
    "Maple",
    "Biscuit",
    "Olive",
    "Rex",
    "Pumpkin",
    "Shadow",
    "Cleo",
    "Oreo",
    "Mochi",
    "Peanut",
    "Scout",
    "Winnie",
    "Archie",
    "Apollo",
    "Atlas",
    "Bandit",
    "Banjo",
    "Baxter",
    "Benny",
    "Blue",
    "Bo",
    "Boomer",
    "Brody",
    "Buster",
    "Captain",
    "Chance",
    "Chester",
    "Chewie",
    "Chico",
    "Cosmo",
    "Diesel",
    "Dixie",
    "Domino",
    "Ellie",
    "Ember",
    "Fiona",
    "Frankie",
    "George",
    "Gizmo",
    "Goose",
    "Gracie",
    "Hank",
    "Harley",
    "Honey",
    "Indy",
    "Ivy",
    "Jack",
    "Jake",
    "Juno",
    "Kiki",
    "Kona",
    "Lady",
    "Loki",
    "Lulu",
    "Mabel",
    "Maggie",
    "Marley",
    "Minnie",
    "Misty",
    "Moose",
    "Nova",
    "Oscar",
    "Otis",
    "Piper",
    "Pippin",
    "Poppy",
    "Prince",
    "Quincy",
    "Rascal",
    "Remi",
    "Roscoe",
    "Rusty",
    "Sasha",
    "Simba",
    "Sky",
    "Smokey",
    "Sophie",
    "Sparky",
    "Sunny",
    "Teddy",
    "Thor",
    "Tilly",
    "Toby",
    "Trixie",
    "Tux",
    "Waffles",
    "Wally",
    "Xena",
    "Yoshi",
    "Ziggy",
    "Zeus",
    "Duchess",
    "Ace",
    "Bonnie",
    "Clyde",
    "Daisy Mae",
    "Hoss",
    "Jethro",
    "Maverick",
    "Raven",
    "Sable",
    "Tank",
    "Ranger",
    "Butterbean",
    "Cinnamon",
    "Cookie",
    "Muffin",
    "Nugget",
    "Noodle",
    "Pickles",
    "Pretzel",
    "Sprinkles",
    "Taco",
    "Tater Tot",
    "Jellybean",
    "Marshmallow",
    "Cupcake",
    "Nacho",
    "Biscotti",
    "Dumpling",
    "Meatball",
    "Pancake",
    "Toffee",
    "Salem",
    "Midnight",
    "Smudge",
    "Socks",
    "Mittens",
    "Patches",
    "Whisper",
    "Boots",
    "Jinx",
    "Pixel",
    "Sushi",
    "Mango",
    "Nutmeg",
    "Pebbles",
    "Clover",
    "Hopper",
    "Flopsy",
    "Dandelion",
    "Marigold",
    "Petunia",
    "Basil",
    "Sage",
    "Cotton",
    "Thistle",
    "Kiwi",
    "Peaches",
    "Sunflower",
    "Pip",
    "Polly",
    "Echo",
    "Boudreaux",
    "Gumbo",
    "Beignet",
    "Praline",
    "Tabasco",
    "Roux",
    "Jolie",
    "Bijou",
    "Gator",
    "Jambalaya",
    "Cayenne",
    "Zydeco",
    "Andouille",
    "Boudin",
    "Crawdad",
    "Mardi",
    "Cher",
    "Satsuma",
    "Pecan",
    "Chicory",
    "Sassafras",
    "Remy",
    "Beau",
]
# species -> (weight, max age in years, breeds)
SPECIES = {
    "Dog": (
        50,
        14,
        [
            "Mixed",
            "Golden Retriever",
            "German Shepherd",
            "Bulldog",
            "Beagle",
            "Labrador",
            "Dachshund",
            "Yorkshire Terrier",
            "Rottweiler",
            "Husky",
            "Chihuahua",
            "Great Dane",
            "Cocker Spaniel",
            "Border Collie",
            "Catahoula",
        ],
    ),
    "Cat": (
        35,
        16,
        [
            "Domestic Shorthair",
            "Domestic Longhair",
            "Siamese",
            "Maine Coon",
            "Tabby",
            "Persian",
            "Bengal",
            "Russian Blue",
        ],
    ),
    "Rabbit": (8, 9, ["Mixed", "Holland Lop", "Mini Rex", "Lionhead", "Netherland Dwarf"]),
    "Bird": (7, 12, ["Parakeet", "Cockatiel", "Lovebird", "Canary", "Conure"]),
}
PET_STATUSES = ["Available", "Pending", "Adopted"]
PET_STATUS_WEIGHTS = [40, 25, 35]
TRANSFER_REASONS = [
    "Overcrowding",
    "Medical Care",
    "Better Adoption Chances",
    "Behavioral Training",
    "Foster Program",
]

VACCINATION_STATUSES = ["Not Vaccinated", "Partial", "Up to Date"]

TREATMENTS = {
    "Dog": [
        "Rabies vaccine",
        "DHPP vaccine",
        "Bordetella vaccine",
        "Deworming",
        "Flea and tick treatment",
        "Heartworm test",
        "Microchip implant",
        "Spay/neuter surgery",
        "Dental cleaning",
        "Antibiotics for skin infection",
    ],
    "Cat": [
        "Rabies vaccine",
        "FVRCP vaccine",
        "FeLV/FIV test",
        "Deworming",
        "Flea treatment",
        "Microchip implant",
        "Spay/neuter surgery",
        "Dental cleaning",
        "Ear mite treatment",
    ],
    "Rabbit": [
        "RHDV2 vaccine",
        "Nail trim",
        "Spay/neuter surgery",
        "Dental check",
        "Parasite treatment",
    ],
    "Bird": [
        "Beak and nail trim",
        "Psittacosis test",
        "Parasite treatment",
        "Vitamin supplement",
        "Feather condition check",
    ],
}

VISIT_NOTES = [
    "Healthy, good weight",
    "Mildly underweight; increase feeding",
    "Shy but cooperative during exam",
    "Minor skin irritation",
    "Recovering well",
    "Cleared for adoption",
    "Recheck in two weeks",
    "Mild dental tartar noted",
    "Energetic and friendly",
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
        raise ValueError(f"No stems left for a shelter in {city}: add more SHELTER_ADJECTIVES")
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

    # bigger city -> bigger shelter (weight 1 ~ 8, weight 8 ~ 29), clamped to 8-30
    weight = CITY_INFO[city][0]
    capacity = max(MIN_CAPACITY, min(MAX_CAPACITY, 5 + 3 * weight + random.randint(-3, 3)))
    shelters.append(
        (
            s_id,
            name,
            f"{random.randint(100, 9999)} {random.choice(ROAD_NAMES)}",
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


# ---------- adopter ----------
adopters = []
used_emails = set()  # Email is Adopter's primary key, so it must be unique
while len(adopters) < NUM_ADOPTERS:
    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)
    email = f"{first.lower()}{last.lower()}{random.randint(1, 99)}@{random.choice(EMAIL_DOMAINS)}"
    if email in used_emails:
        continue  # collision: skip it and generate another person
    used_emails.add(email)

    # adopters live anywhere, but more of them in bigger cities
    city = random.choices(CITIES, weights=CITY_WEIGHTS)[0]
    address = f"{random.randint(100, 9999)} {random.choice(ROAD_NAMES)}, {city}, LA"
    adopters.append((email, first, last, address, random_phone(city)))

conn.executemany(
    "INSERT INTO Adopter (Email, FirstName, LastName, Address, PhoneNumber) VALUES (?, ?, ?, ?, ?)", adopters
)

adopter_emails = [a[0] for a in adopters]  # the Application section picks from these


# ---------- pet ----------
species_names = list(SPECIES)
species_weights = [SPECIES[s][0] for s in species_names]

pets = []
for p_id in make_ids(NUM_PETS):
    species = random.choices(species_names, weights=species_weights)[0]
    _, max_age, breeds = SPECIES[species]
    status = random.choices(PET_STATUSES, weights=PET_STATUS_WEIGHTS)[0]

    # busier shelters take in more animals; this is what makes some shelters overcrowded
    shelter_id = random.choices(shelter_ids, weights=shelter_intake_weights)[0]

    # Pending/Adopted pets need time after intake for applications (and an adoption),
    # so they must have arrived at least 30 days before TODAY
    latest_intake = TODAY if status == "Available" else TODAY - timedelta(days=30)
    taken_in = random_date(date(2025, 1, 1), latest_intake)
    birth = taken_in - timedelta(days=random.randint(60, max_age * 365))  # at least ~2 months old at intake

    pets.append(
        (
            p_id,
            shelter_id,
            random.choice(PET_NAMES),
            species,
            random.choice(breeds),
            birth.isoformat(),
            random.choice(["Male", "Female"]),
            status,
            taken_in.isoformat(),
        )
    )

conn.executemany(
    "INSERT INTO Pet (ID, Shelter_ID, Name, Species, Breed, BirthDate, Sex, AdoptionStatus, DateTakenIn) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
    pets,
)


# ---------- staff ----------
shelter_slugs = {s[0]: re.sub(r"[^a-z0-9]+", "-", s[1].lower()).strip("-") for s in shelters}
shelter_city = {s[0]: s[3] for s in shelters}

# every shelter gets one of each role; bigger shelters get an extra Intake (20+) and an extra Vet (25+)
staff_roles = []
for s in shelters:
    s_id, capacity = s[0], s[6]
    roles = ["Intake", "Vet", "Coordinator"]
    if capacity >= 20:
        roles.append("Intake")
    if capacity >= 25:
        roles.append("Vet")
    staff_roles += [(s_id, role) for role in roles]

staff = []
used_staff_emails = set()
vets_at = {s_id: [] for s_id in shelter_ids}  # shelter -> its vets' IDs (MedicalRecords picks from these)
for st_id, (s_id, role) in zip(make_ids(len(staff_roles)), staff_roles):
    while True:
        first, last = random.choice(FIRST_NAMES), random.choice(LAST_NAMES)
        email = f"{first.lower()}.{last.lower()}@{shelter_slugs[s_id]}.org"
        if email not in used_staff_emails:
            break
    used_staff_emails.add(email)
    staff.append((st_id, s_id, f"{first} {last}", role, email, random_phone(shelter_city[s_id])))
    if role == "Vet":
        vets_at[s_id].append(st_id)

conn.executemany("INSERT INTO Staff (ID, Shelter_ID, Name, Role, Email, PhoneNumber) VALUES (?, ?, ?, ?, ?, ?)", staff)


# ---------- transfer ----------
capacity_of = {s[0]: s[6] for s in shelters}
housed = {s_id: 0 for s_id in shelter_ids}  # pets currently in each shelter (Adopted pets have left)
for p in pets:
    if p[7] != "Adopted":
        housed[p[1]] += 1

pet_intake_shelter = {p[0]: p[1] for p in pets}
pet_moves = {p[0]: [] for p in pets}  # pet ID -> list of (date, from_shelter, to_shelter), oldest first


def current_shelter(p_id):
    """The shelter holding the pet after all its transfers."""
    moves = pet_moves[p_id]
    return moves[-1][2] if moves else pet_intake_shelter[p_id]


def shelter_at(p_id, day):
    """The shelter that held the pet on a given day (a date object)."""
    shelter = pet_intake_shelter[p_id]
    for move_day, _, to_shelter in pet_moves[p_id]:
        if move_day <= day:
            shelter = to_shelter
    return shelter


transfers = []


def record_transfer(p_id, day, to_shelter, reason):
    from_shelter = current_shelter(p_id)
    pet_moves[p_id].append((day, from_shelter, to_shelter))
    transfers.append((p_id, from_shelter, to_shelter, day.isoformat(), reason))


# 1) recent transfers out of overcrowded shelters, into shelters with free space
for s_id in shelter_ids:
    over = housed[s_id] - capacity_of[s_id]
    if over <= 0:
        continue
    candidates = [p for p in pets if p[1] == s_id and p[7] == "Available"]
    for p in random.sample(candidates, min(over, random.randint(2, 4), len(candidates))):
        open_shelters = [t for t in shelter_ids if t != s_id and housed[t] < capacity_of[t]]
        to_shelter = random.choice(open_shelters)
        start = max(date.fromisoformat(p[8]), TODAY - timedelta(days=60))
        record_transfer(p[0], random_date(start, TODAY), to_shelter, "Overcrowding")
        housed[s_id] -= 1
        housed[to_shelter] += 1

# 2) for past transfers of pets that were later adopted (1 or 2 moves, all before TODAY - 20 days
# so the application and adoption can come after the last move)
adopted_pets = [p for p in pets if p[7] == "Adopted"]
for p in random.sample(adopted_pets, round(len(adopted_pets) * HISTORICAL_TRANSFER_SHARE)):
    day = date.fromisoformat(p[8])
    latest = TODAY - timedelta(days=20)
    for _ in range(2 if random.random() < 0.2 else 1):
        if day + timedelta(days=1) > latest:
            break
        day = random_date(day + timedelta(days=1), latest)
        to_shelter = random.choice([t for t in shelter_ids if t != current_shelter(p[0])])
        record_transfer(p[0], day, to_shelter, random.choice(TRANSFER_REASONS))

conn.executemany(
    "INSERT INTO Transfer (Pet_ID, From_Shelter_ID, To_Shelter_ID, Date, Reason) VALUES (?, ?, ?, ?, ?)", transfers
)

# a transfer changes where the pet is: update Pet.Shelter_ID, and keep the Python copy in sync
moved = [(current_shelter(p_id), p_id) for p_id, moves in pet_moves.items() if moves]
conn.executemany("UPDATE Pet SET Shelter_ID = ? WHERE ID = ?", moved)
pets = [(p[0], current_shelter(p[0])) + p[2:] for p in pets]

# ---------- application ----------
app_count = {email: 0 for email in adopter_emails}  # applications per adopter so far


def pick_adopter(applicants):
    """An adopter with room for another application who hasn't applied for this pet yet."""
    choices = [e for e in adopter_emails if app_count[e] < MAX_APPS_PER_ADOPTER and e not in applicants]
    email = random.choice(choices)
    app_count[email] += 1
    applicants.add(email)
    return email


app_rows = []  # (date, pet ID, adopter email, handling shelter, status); IDs are assigned after sorting by date


def add_application(p_id, day, status, applicants):
    app_rows.append((day, p_id, pick_adopter(applicants), shelter_at(p_id, day), status))


for p in pets:
    p_id, pet_status, taken_in = p[0], p[7], date.fromisoformat(p[8])
    moves = pet_moves[p_id]
    settled = moves[-1][0] + timedelta(days=1) if moves else taken_in  # arrived at its final shelter
    applicants = set()  # adopters who already applied for this pet

    if pet_status in ("Adopted", "Pending"):
        # the application that made the pet Pending/Adopted comes after its last transfer;
        # Adopted pets need room after it for the adoption itself
        latest = TODAY - timedelta(days=15) if pet_status == "Adopted" else TODAY
        main_day = random_date(settled, latest)
        if random.random() < DENIED_BEFORE_CHANCE and main_day > taken_in:
            add_application(p_id, random_date(taken_in, main_day - timedelta(days=1)), "Denied", applicants)
        add_application(p_id, main_day, "Approved" if pet_status == "Adopted" else "Pending", applicants)
    elif random.random() < DENIED_AVAILABLE_CHANCE:
        add_application(p_id, random_date(taken_in, TODAY), "Denied", applicants)

# number applications in date order, like a real system handing out IDs as they arrive
app_rows.sort(key=lambda row: row[0])
applications = [
    (a_id, p_id, email, s_id, status, day.isoformat())
    for a_id, (day, p_id, email, s_id, status) in zip(make_ids(len(app_rows)), app_rows)
]
conn.executemany(
    "INSERT INTO Application (ID, Pet_ID, Adopter_Email, Shelter_ID, Status, Date) VALUES (?, ?, ?, ?, ?, ?)",
    applications,
)

# ---------- adoption ----------
pet_by_id = {p[0]: p for p in pets}
adoptions = []
adoption_day = {}  # pet ID -> adoption date (MedicalRecords needs it: no vet visits after a pet leaves)
for a_id, p_id, _, _, status, day in applications:
    if status != "Approved":
        continue
    adopted_on = min(date.fromisoformat(day) + timedelta(days=random.randint(1, 14)), TODAY)
    species, birth = pet_by_id[p_id][3], date.fromisoformat(pet_by_id[p_id][5])
    fee = ADOPTION_FEES[species]
    if (adopted_on - birth).days >= SENIOR_AGE * 365:
        fee /= 2
    adoptions.append((a_id, adopted_on.isoformat(), fee))
    adoption_day[p_id] = adopted_on
conn.executemany("INSERT INTO Adoption (Application_ID, Date, Fee) VALUES (?, ?, ?)", adoptions)

# ---------- medical records ----------
medical_records = []
for p in pets:
    p_id, species, taken_in = p[0], p[3], date.fromisoformat(p[8])
    last_day = adoption_day.get(p_id, TODAY)  # no visits after the pet goes home

    # first visit is the intake exam within 3 days of arrival; later visits fall anywhere after it
    first_visit = min(taken_in + timedelta(days=random.randint(0, 3)), last_day)
    n_visits = random.choices([1, 2, 3, 4], weights=VISIT_COUNT_WEIGHTS)[0]
    visit_days = sorted([first_visit] + [random_date(first_visit, last_day) for _ in range(n_visits - 1)])

    # give each visit a time; (date, time) must be unique per pet because it's part of the primary key
    visits = set()
    for day in visit_days:
        while True:
            visit_time = f"{random.randint(8, 16):02d}:{random.choice(['00', '15', '30', '45'])}"
            if (day, visit_time) not in visits:
                break
        visits.add((day, visit_time))

    vaccination_level = random.choices([0, 1, 2], weights=[40, 30, 30])[0]  # index into VACCINATION_STATUSES
    for i, (day, visit_time) in enumerate(sorted(visits)):  # oldest first, including same-day visits
        if i > 0 and vaccination_level < 2 and random.random() < 0.7:
            vaccination_level += 1  # follow-up visits usually catch vaccinations up; never goes backward

        treatments = "; ".join(random.sample(TREATMENTS[species], random.randint(1, 2)))
        notes = "Intake exam" if i == 0 else random.choice(VISIT_NOTES + [None])
        vet_id = random.choice(vets_at[shelter_at(p_id, day)])  # a vet at the shelter holding the pet that day
        medical_records.append(
            (p_id, day.isoformat(), visit_time, VACCINATION_STATUSES[vaccination_level], notes, treatments, vet_id)
        )

conn.executemany(
    "INSERT INTO MedicalRecords (Pet_ID, Date, Time, VaccinationStatus, Notes, Treatments, Vet_ID) "
    "VALUES (?, ?, ?, ?, ?, ?, ?)",
    medical_records,
)


conn.commit()
conn.close()

print(f"\nShelters: {len(shelters)}\nAdopters: {len(adopters)}\nPets: {len(pets)}\nStaff: {len(staff)}")
print(f"Transfers: {len(transfers)}\nApplications: {len(applications)}\nAdoptions: {len(adoptions)}")
print(f"Medical records: {len(medical_records)}\n")
