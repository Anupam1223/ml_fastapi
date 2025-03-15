from fastapi import FastAPI
import joblib
import numpy as np
from app.schemas import InputData

app = FastAPI()

model = joblib.load("model.pkl")


@app.post("/predict")
def predict(data: InputData):
    prediction = model.predict([np.array(data.features)])
    return {"prediction": prediction.tolist()}
