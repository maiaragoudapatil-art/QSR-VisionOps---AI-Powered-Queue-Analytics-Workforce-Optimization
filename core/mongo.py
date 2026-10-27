from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017/"
)

db = client["qsr_visionops"]

analytics_archive = db["analytics_archive"]