from joblib import load
import pandas as pd

model = load("ml/model.joblib")

def predict_price(vehicle):
    df = pd.DataFrame([{
        "year": vehicle.get("year", 0),
        "mileage_km": vehicle.get("mileage_km", 0)
    }])
    return int(model.predict(df)[0])