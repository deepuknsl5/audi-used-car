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

        vehicle["last_seen"] = now

        result = vehicles_col.update_one(
            {"vin": vin},
            {
                "$set": vehicle,
                "$setOnInsert": {"created_at": now}
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
                    "status": "inactive",
                    "last_seen": now
                }
            }
        )
        removed = len(removed_vins)

    # 🧾 LOG SYNC
    sync_logs_col.insert_one({
        "sync_time": now,
        "added": added,
        "updated": updated,
        "removed": removed,
        "total_active": vehicles_col.count_documents({"status": "active"})
    })

    print(
        f"✅ Sync complete | Added: {added}, Updated: {updated}, Removed: {removed}"
    )


if __name__ == "__main__":
    asyncio.run(run_sync())