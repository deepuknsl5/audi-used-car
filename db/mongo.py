from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DB_NAME")]

vehicles_col = db.vehicles
sync_logs_col = db.sync_logs
ml_metrics_col = db.ml_metrics

vehicles_col.create_index("vin", unique=True)
vehicles_col.create_index("status")