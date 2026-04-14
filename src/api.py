from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
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

@app.post("/predict")
def predict(data: SunVector):
    x = pd.DataFrame([{
        "sun_x": data.sun_x,
        "sun_y": data.sun_y,
        "sun_z": data.sun_z
    }])

    prediction = model.predict(x)[0]

    return {
        "predicted_zenith": float(prediction)
    }