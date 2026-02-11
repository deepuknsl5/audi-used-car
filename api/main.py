from fastapi import FastAPI, BackgroundTasks
from db.mongo import vehicles_col, sync_logs_col
from ml.predict import predict_price
from ml.train import train_model
from sync.sync_engine import run_sync
import asyncio

app = FastAPI()

def run_pipeline():
    """Runs scrape + sync + ML training"""
    asyncio.run(run_sync())
    train_model()
    
@app.get("/vehicles")
def get_vehicles():
    return list(vehicles_col.find({"status": "active"}, {"_id": 0}))

@app.get("/vehicles/{vin}/predict")
def get_prediction(vin: str):
    vehicle = vehicles_col.find_one({"vin": vin})
    pred = predict_price(vehicle)
    return {
        "vin": vin,
        "actual_price": vehicle["price"],
        "predicted_price": pred
    }

@app.get("/sync-status")
def sync_status():
    log = sync_logs_col.find_one(sort=[("sync_time", -1)])

    if not log:
        return {
            "message": "No sync has been completed yet",
            "last_sync": None,
            "added": 0,
            "updated": 0,
            "removed": 0,
            "total_active": 0
        }

    return {
        "last_sync": log.get("sync_time"),
        "added": log.get("added", 0),
        "updated": log.get("updated", 0),
        "removed": log.get("removed", 0),
        "total_active": log.get("total_active", 0)
    }

@app.post("/trigger-sync")
def trigger_sync(background_tasks: BackgroundTasks):
    """
    Trigger inventory sync and ML retraining.
    This endpoint returns immediately.
    """
    background_tasks.add_task(run_pipeline)
    return {"status": "sync started"}