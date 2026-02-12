# from fastapi import FastAPI, BackgroundTasks, HTTPException
# from db.mongo import vehicles_col, sync_logs_col
# from ml.predict import predict_price
# from ml.train import train_model
# from sync.sync_engine import run_sync
# import asyncio

# app = FastAPI(title="Audi Used Car Inventory API")

# # -----------------------------
# # Background pipeline (SAFE)
# # -----------------------------

# async def async_pipeline():
#     """Async-safe pipeline: scrape + sync"""
#     await run_sync()

# def run_pipeline():
#     """
#     Wrapper for FastAPI BackgroundTasks.
#     Uses asyncio.create_task instead of asyncio.run.
#     """
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(async_pipeline())
#     train_model()


# # -----------------------------
# # API Endpoints
# # -----------------------------

# @app.get("/vehicles")
# def get_vehicles():
#     return list(vehicles_col.find({"status": "active"}, {"_id": 0}))


# @app.get("/vehicles/{vin}/predict")
# def get_prediction(vin: str):
#     vehicle = vehicles_col.find_one({"vin": vin})

#     if not vehicle:
#         raise HTTPException(status_code=404, detail="Vehicle not found")

#     try:
#         predicted_price = predict_price(vehicle)
#     except FileNotFoundError:
#         raise HTTPException(
#             status_code=503,
#             detail="Model not trained yet. Please run /trigger-sync first."
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

#     return {
#         "vin": vin,
#         "actual_price": vehicle["price"],
#         "predicted_price": predicted_price,
#         "difference": predicted_price - vehicle["price"]
#     }


# @app.get("/sync-status")
# def sync_status():
#     log = sync_logs_col.find_one(sort=[("sync_time", -1)])

#     if not log:
#         return {
#             "message": "No sync has been completed yet",
#             "last_sync": None,
#             "added": 0,
#             "updated": 0,
#             "removed": 0,
#             "total_active": 0
#         }

#     return {
#         "last_sync": log.get("sync_time"),
#         "added": log.get("added", 0),
#         "updated": log.get("updated", 0),
#         "removed": log.get("removed", 0),
#         "total_active": log.get("total_active", 0)
#     }


# @app.post("/trigger-sync")
# def trigger_sync(background_tasks: BackgroundTasks):
#     """
#     Trigger inventory sync and ML retraining.
#     Returns immediately.
#     """
#     background_tasks.add_task(run_pipeline)
#     return {"status": "sync + training started"}

from fastapi import FastAPI, BackgroundTasks, HTTPException
from db.mongo import vehicles_col, sync_logs_col, ml_metrics_col
from ml.predict import predict_price
from ml.train import train_model
from sync.sync_engine import run_sync
from datetime import datetime
import asyncio

app = FastAPI(title="Audi Used Car Inventory API")

# -------------------------------------------------
# Background pipeline
# -------------------------------------------------

async def async_pipeline():
    await run_sync()

def run_pipeline():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(async_pipeline())
    train_model()

# -------------------------------------------------
# API Endpoints
# -------------------------------------------------

@app.get("/vehicles")
def get_vehicles():
    vehicles = list(
        vehicles_col.find({"status": "active"}, {"_id": 0})
    )

    # Convert datetime fields to ISO
    for v in vehicles:
        if v.get("date_scraped"):
            v["date_scraped"] = v["date_scraped"].isoformat()
        if v.get("last_seen"):
            v["last_seen"] = v["last_seen"].isoformat()

    return vehicles


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
    log = sync_logs_col.find_one(sort=[("timestamp", -1)])

    if not log:
        return {
            "message": "No sync completed yet",
            "last_sync": None,
            "new_added": 0,
            "updated": 0,
            "removed": 0,
            "total_active": 0
        }

    return {
        "last_sync": log.get("timestamp").isoformat() if log.get("timestamp") else None,
        "new_added": log.get("new_count", 0),
        "updated": log.get("updated_count", 0),
        "removed": log.get("removed_count", 0),
        "total_active": log.get("total_active", 0)
    }


@app.post("/trigger-sync")
def trigger_sync(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_pipeline)
    return {"status": "sync + training started"}


# -------------------------------------------------
# FINAL REQUIRED: /report Endpoint
# -------------------------------------------------

@app.get("/report")
def get_report():

    # 1️⃣ Active Vehicles
    vehicles_cursor = vehicles_col.find(
        {"status": "active"},
        {"_id": 0}
    ).sort("price", 1)

    vehicles = []

    for v in vehicles_cursor:
        if v.get("date_scraped"):
            v["date_scraped"] = v["date_scraped"].isoformat()
        if v.get("last_seen"):
            v["last_seen"] = v["last_seen"].isoformat()

        # Add predicted price if model exists
        try:
            predicted = predict_price(v)
            v["predicted_price"] = predicted
            v["price_difference"] = predicted - v["price"]
        except:
            v["predicted_price"] = None
            v["price_difference"] = None

        vehicles.append(v)

    total_active = len(vehicles)

    # 2️⃣ Latest Sync Info
    latest_sync = sync_logs_col.find_one(sort=[("timestamp", -1)])

    sync_section = {
        "Last Sync": latest_sync["timestamp"].isoformat() if latest_sync else None,
        "New Vehicles Added": latest_sync.get("new_count", 0) if latest_sync else 0,
        "Vehicles Updated": latest_sync.get("updated_count", 0) if latest_sync else 0,
        "Vehicles Removed": latest_sync.get("removed_count", 0) if latest_sync else 0,
        "Total Active": total_active
    }

    # 3️⃣ Latest ML Metrics
    latest_ml = ml_metrics_col.find_one(sort=[("timestamp", -1)])

    if latest_ml:
        last_trained = (
            latest_ml.get("timestamp").isoformat()
            if latest_ml.get("timestamp")
            else None
        )

        ml_section = {
            "Model Used": latest_ml.get("model_name"),
            "Features": latest_ml.get("features", []),
            "MAE": latest_ml.get("mae"),
            "RMSE": latest_ml.get("rmse"),
            "R2 Score": latest_ml.get("r2_score"),
            "Last Trained": last_trained
        }
    else:
        ml_section = {
            "Model Used": None,
            "Features": [],
            "MAE": None,
            "RMSE": None,
            "R2 Score": None,
            "Last Trained": None
        }

    automation_section = {
        "Trigger": "Every 24 Hours",
        "Manual Trigger Endpoint": "/trigger-sync",
        "Status": "Operational"
    }

    return {
        "Company": "Audi West Island",
        "Total Vehicles": total_active,
        "Vehicles": vehicles,
        "Database Sync": sync_section,
        "ML Price Prediction": ml_section,
        "Automation": automation_section
    }