# Builds the API using FastAPI using the model in
# production available on mlflow

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import numpy as np
import json
import mlflow
import warnings
warnings.filterwarnings('ignore')

# defines the mlflow model's url in mlflow
# and defines the production model
mlflow.set_tracking_uri("http://mlflow:5000")

try: 
    production_model = mlflow.pyfunc.load_model("models:/regression_model/Production")

except Exception as e:
        print(f"An error occurred during loading prod model from mlflow: {str(e)}")

# Defining the API using FastAPI
tags_metadata = [{"name": "fraud-detect", "description": "Fraudulent Transaction Detection API"}]
app = FastAPI(title = "Fraud Detection API",
              description = "Fraudulent Transaction Detection API",
              version = "1.0",
              contact = {"name": "Artur"},
              openapi_tags = tags_metadata)

# Data validation to be applied on
# the data that comes from the json payload
class Features(BaseModel):
    bath: float
    beds: float
    propertysqft: float
    latitude: float
    longitude: float

@app.get("/")
def message():
    text = "API for fraudulent transactions detection in the financial institution"
    return text

@app.post("/predict", tags = ["Predict_Fraud"])
async def predict(Features: Features):

    X_data = Features.model_dump_json()
    X_data_dict = json.loads(X_data)
    
    bath = X_data_dict["bath"]
    beds = X_data_dict["beds"]
    propertysqft = X_data_dict["propertysqft"]
    latitude = X_data_dict["latitude"]
    longitude = X_data_dict["longitude"]

    features = [bath, beds, propertysqft, latitude, longitude]
    input = pd.DataFrame(np.array(features).reshape(1,-1), columns=["bath", "beds", "propertysqft", "latitude", "longitude"])

    y_pred_price = production_model.predict(input)

    response = {"predicted_price": y_pred_price[0]}
    
    return response

if __name__ == "__main__":
    uvicorn.run(app, host = "0.0.0.0", port = 3000)
