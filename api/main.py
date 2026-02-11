from fastapi import FastAPI, BackgroundTasks, HTTPException
from db.mongo import vehicles_col, sync_logs_col
from ml.predict import predict_price
from ml.train import train_model
from sync.sync_engine import run_sync
import asyncio

app = FastAPI(title="Audi Used Car Inventory API")

# -----------------------------
# Background pipeline (SAFE)
# -----------------------------

async def async_pipeline():
    """Async-safe pipeline: scrape + sync"""
    await run_sync()

def run_pipeline():
    """
    Wrapper for FastAPI BackgroundTasks.
    Uses asyncio.create_task instead of asyncio.run.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_pipeline())
    train_model()


# -----------------------------
# API Endpoints
# -----------------------------

@app.get("/vehicles")
def get_vehicles():
    return list(vehicles_col.find({"status": "active"}, {"_id": 0}))


@app.get("/vehicles/{vin}/predict")
def get_prediction(vin: str):
    vehicle = vehicles_col.find_one({"vin": vin})

    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    try:
        predicted_price = predict_price(vehicle)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Please run /trigger-sync first."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "vin": vin,
        "actual_price": vehicle["price"],
        "predicted_price": predicted_price,
        "difference": predicted_price - vehicle["price"]
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
    Returns immediately.
    """
    background_tasks.add_task(run_pipeline)
    return {"status": "sync + training started"}