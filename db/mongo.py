# db/mongo.py
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise RuntimeError("MONGO_URI not set")

client = MongoClient(MONGO_URI)

# ✅ Use database from URI (no DB_NAME needed)
db = client.get_default_database()

vehicles_col = db["vehicles"]
sync_logs_col = db["sync_logs"]
ml_metrics_col = db["ml_metrics"]
 
 
# import os
# from pymongo import MongoClient
# from dotenv import load_dotenv

# load_dotenv()  # Load .env file

# MONGO_URI = os.getenv("MONGO_URI")

# if not MONGO_URI:
#     raise RuntimeError("MONGO_URI not set")

# client = MongoClient(MONGO_URI)

# db = client.get_default_database()

# vehicles_col = db["vehicles"]
# sync_logs_col = db["sync_logs"]
# ml_metrics_col = db["ml_metrics"]