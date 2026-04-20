from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "solar_tracking_model.pkl"

model = joblib.load(MODEL_PATH)


class SunVector(BaseModel):
    sun_x: float
    sun_y: float
    sun_z: float


@app.get("/")
def home():
    return {"message": "Solar Tracking API is running"}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def calculate_required_zenith(sx, sy, sz):
    sun = np.array([sx, sy, sz], dtype=float)
    norm = np.linalg.norm(sun)

    if norm == 0:
        return 0.0

    sun_z_normalized = sun[2] / norm
    sun_z_normalized = np.clip(sun_z_normalized, -1.0, 1.0)

    zenith_deg = np.degrees(np.arccos(sun_z_normalized))
    return float(zenith_deg)


@app.post("/predict")
def predict(data: SunVector):
    x = pd.DataFrame([{
        "sun_x": data.sun_x,
        "sun_y": data.sun_y,
        "sun_z": data.sun_z
    }])

    prediction = model.predict(x)[0]

    analytic_zenith = calculate_required_zenith(
        data.sun_x,
        data.sun_y,
        data.sun_z
    )

    print("INPUT:")
    print(x)

    print("ML PREDICTION:")
    print(prediction)

    print("ANALYTIC ZENITH:")
    print(analytic_zenith)

    return {
        "predicted_zenith": float(prediction),
        "analytic_zenith": analytic_zenith
    }