from scraper.scrape_inventory import scrape_inventory
from db.mongo import vehicles_col, sync_logs_col
from datetime import datetime, timezone
import asyncio

async def run_sync():
    now = datetime.now(timezone.utc)

    print("🔄 Running inventory sync...")

    scraped = await scrape_inventory()
    scraped_map = {v["vin"]: v for v in scraped}

    db_vins = set(vehicles_col.distinct("vin"))
    scraped_vins = set(scraped_map.keys())

    added = updated = removed = 0

    # ✅ ADD / UPDATE VEHICLES
    for vin, vehicle in scraped_map.items():

        # 🔐 PRICE NORMALIZATION (CRITICAL FIX)
        if "price" in vehicle and vehicle["price"] is not None:
            # If price looks like cents (e.g. 3379500), fix it
            if vehicle["price"] > 1_000_000:
                vehicle["price"] = int(vehicle["price"] / 100)

        # vehicle_update = vehicle.copy()

        # Always update last_seen
        # vehicle_update["last_seen"] = now
        # vehicle_update["status"] = "active"

        vehicle_update = vehicle.copy()
        vehicle_update.pop("date_scraped", None)

        result = vehicles_col.update_one(
            {"vin": vin},
            {
                "$set": {
                    **vehicle_update,
                    "last_seen": now,
                    "status": "active"
                },
                "$setOnInsert": {
                    "date_scraped": now
                }
            },
            upsert=True
        )
        if result.upserted_id:
            added += 1
        elif result.modified_count:
            updated += 1

    # 🚫 MARK REMOVED VEHICLES
    removed_vins = db_vins - scraped_vins
    if removed_vins:
        vehicles_col.update_many(
            {"vin": {"$in": list(removed_vins)}},
            {
                "$set": {
                    "status": "inactive"
                  
                }
            }
        )
        removed = len(removed_vins)

    # 🧾 LOG SYNC
    sync_logs_col.insert_one({
    "timestamp": now,
    "new_count": added,
    "updated_count": updated,
    "removed_count": removed,
    "total_active": vehicles_col.count_documents({"status": "active"})
})

    print(
        f"✅ Sync complete | Added: {added}, Updated: {updated}, Removed: {removed}"
    )


if __name__ == "__main__":
    asyncio.run(run_sync())