# ml/predict.py
import os
import pandas as pd
import numpy as np
from joblib import load

MODEL_PATH = "ml/model.joblib"
_model = None


def get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError("ML model not trained yet")
        _model = load(MODEL_PATH)
    return _model


def predict_price(vehicle: dict) -> float:
    model = get_model()

    X = np.array([[
        vehicle["year"],
        vehicle["mileage_km"]
    ]])

    return float(model.predict(X)[0])