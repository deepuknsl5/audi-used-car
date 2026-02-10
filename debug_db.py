from db.mongo import vehicles_col
from db.mongo import ml_metrics_col
print(ml_metrics_col.find_one(sort=[("trained_at", -1)]))
print("🔍 Checking MongoDB vehicles collection...\n")

doc = vehicles_col.find_one()

if not doc:
    print("❌ No documents found in vehicles collection.")
else:
    print("✅ Sample vehicle document:\n")
    for k, v in doc.items():
        print(f"{k}: {v}")