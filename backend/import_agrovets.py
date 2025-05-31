import csv
from pymongo import MongoClient
import logging
from config import Config, geolocation_collection, agrovets_collection
from fuzzywuzzy import process
import random

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB Configuration
MONGO_URI = Config.MONGO_URI
DB_NAME = "crophealthai"

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
agrovets_collection = db.get_collection("agrovets")
geolocation_collection = db.get_collection("geolocation")

# Ensure geospatial index is created
if agrovets_collection is not None:
    agrovets_collection.create_index([("location", "2dsphere")])

if geolocation_collection is not None:
    geolocation_collection.create_index([("location", "2dsphere")])

# Path to the CSV file
CSV_FILE_PATH = "agrovets.csv"

# Function to find the closest match for county and town
def find_closest_match(query, choices):
    if not choices:
        return None
    # Perform fuzzy matching with a case-insensitive comparison
    closest_match, score = process.extractOne(query.lower(), [choice.lower() for choice in choices])
    if score >= 80:  # Threshold for considering a match
        return closest_match.title()  # Return the match in title case
    return None

# Function to insert agrovets data into MongoDB
def insert_agrovets_data():
    try:
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))  # Read all rows into a list
            if len(reader) < 2000:
                logging.warning(f"⚠️ Only {len(reader)} entries found in the CSV file. Using all available entries.")
                sampled_rows = reader
            else:
                sampled_rows = random.sample(reader, 2000)  # Randomly sample 2000 entries

            data_to_insert = []
            geolocation_to_insert = []

            # Fetch distinct counties and towns from geolocation collection
            counties = geolocation_collection.distinct("county")
            towns = geolocation_collection.distinct("town")

            for row in sampled_rows:
                name = row.get("name")
                county = row.get("county")
                town = row.get("town")
                latitude = float(row.get("latitude"))
                longitude = float(row.get("longitude"))
                contact = row.get("contact")

                if not name or not county or not town or not latitude or not longitude or not contact:
                    logging.warning(f"⚠️ Incomplete data for row: {row}. Skipping.")
                    continue

                # Find closest matches for county and town
                closest_county = find_closest_match(county, counties)
                closest_town = find_closest_match(town, towns)

                if not closest_county or not closest_town:
                    logging.warning(f"⚠️ No close match found for {name} in {town}, {county}. Skipping.")
                    continue

                # Check if geolocation already exists
                geolocation = geolocation_collection.find_one({"county": closest_county, "town": closest_town})
                if not geolocation:
                    logging.warning(f"⚠️ Geolocation not found for {name} in {closest_town}, {closest_county}. Adding new geolocation data.")
                    geolocation_to_insert.append({
                        "county": closest_county,
                        "town": closest_town,
                        "location": {
                            "type": "Point",
                            "coordinates": [longitude, latitude]
                        }
                    })
                    geolocation = geolocation_to_insert[-1]

                if geolocation:
                    data_to_insert.append({
                        "name": name,
                        "county": closest_county,
                        "town": closest_town,
                        "location": geolocation["location"],
                        "contact": contact
                    })

                # Insert geolocation data in batches
                if len(geolocation_to_insert) >= 100:
                    geolocation_collection.insert_many(geolocation_to_insert)
                    logging.info(f"✅ Inserted {len(geolocation_to_insert)} new geolocation entries.")
                    geolocation_to_insert.clear()

                # Insert agrovets data in batches
                if len(data_to_insert) >= 1000:
                    agrovets_collection.insert_many(data_to_insert)
                    logging.info(f"✅ Inserted {len(data_to_insert)} new agrovets entries.")
                    data_to_insert.clear()

            # Insert remaining geolocation data
            if geolocation_to_insert:
                geolocation_collection.insert_many(geolocation_to_insert)
                logging.info(f"✅ Inserted {len(geolocation_to_insert)} new geolocation entries.")

            # Insert remaining agrovets data
            if data_to_insert:
                agrovets_collection.insert_many(data_to_insert)
                logging.info(f"✅ Inserted {len(data_to_insert)} new agrovets entries.")

            if not data_to_insert:
                logging.info("⚠️ No agrovets data to insert.")
    except Exception as e:
        logging.error(f"⚠️ Error inserting agrovets data: {e}")

# Run the insertion
if __name__ == "__main__":
    insert_agrovets_data()