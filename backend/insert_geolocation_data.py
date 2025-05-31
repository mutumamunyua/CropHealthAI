import csv
from pymongo import MongoClient
import logging
from config import Config, geolocation_collection

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# MongoDB Configuration
MONGO_URI = Config.MONGO_URI
DB_NAME = "crophealthai"
COLLECTION_NAME = "geolocation"

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
geolocation_collection = db[COLLECTION_NAME]

# Ensure geospatial index is created
geolocation_collection.create_index([("location", "2dsphere")])

# Path to the CSV file
CSV_FILE_PATH = "townske.csv"

# Function to insert geolocation data into MongoDB
def insert_geolocation_data():
    try:
        with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            data_to_insert = [
                {
                    "county": row["County"],
                    "town": row["Town"],
                    "location": {
                        "type": "Point",
                        "coordinates": [float(row["Longitude"]), float(row["Latitude"])]
                    }
                }
                for row in reader
            ]
            geolocation_collection.insert_many(data_to_insert)
            logging.info("✅ Geolocation data inserted successfully.")
    except Exception as e:
        logging.error(f"⚠️ Error inserting geolocation data: {e}")

# Run the insertion
if __name__ == "__main__":
    insert_geolocation_data()