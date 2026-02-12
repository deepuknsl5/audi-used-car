import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from joblib import dump
from db.mongo import vehicles_col, ml_metrics_col
from datetime import datetime, timezone

def train_model():
    data = list(vehicles_col.find({"status": "active"}))
    df = pd.DataFrame(data)

    df = df.dropna(subset=["price", "mileage_km"])
    X = df[["year", "mileage_km"]].fillna(0)
    y = df["price"]

    model = RandomForestRegressor(n_estimators=200, random_state=42)
    model.fit(X, y)
    
    preds = model.predict(X)

    mae = mean_absolute_error(y, preds)
    r2 = r2_score(y, preds)

    dump(model, "ml/model.joblib")

    ml_metrics_col.insert_one({
        "model": "RandomForest",
        "mae": mae,
        "r2": r2,
        "trained_at": datetime.now(timezone.utc)
    })

if __name__ == "__main__":
    train_model()