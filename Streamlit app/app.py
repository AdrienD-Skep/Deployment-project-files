import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Body
import joblib
from pydantic import BaseModel
from typing import List

description = """
This API helps you predict the recommended rental price per day for cars based on their features.
It uses a pre-trained machine learning model to provide accurate price predictions.
"""

app = FastAPI(
    title="🚗 Car Rental Price Prediction API",
    description=description,
    version="1.0"
)

# Load the model with error handling
try:
    model = joblib.load('src/model_XGBR.pkl')
except Exception as e:
    raise RuntimeError(f"Failed to load the model: {e}")

class CarFeatures(BaseModel):
    model_key: str
    mileage: float
    engine_power: float
    fuel: str
    paint_color: str
    car_type: str
    private_parking_available: bool
    has_gps: bool
    has_air_conditioning: bool
    automatic_car: bool
    has_getaround_connect: bool
    has_speed_regulator: bool
    winter_tires: bool
    class Config:
        schema_extra = {
            "example": {
                "model_key": "Peugeot",
                "mileage": 15000.0,
                "engine_power": 120.0,
                "fuel": "diesel",
                "paint_color": "black",
                "car_type": "hatchback",
                "private_parking_available": True,
                "has_gps": True,
                "has_air_conditioning": True,
                "automatic_car": False,
                "has_getaround_connect": True,
                "has_speed_regulator": True,
                "winter_tires": False
            }
        }

@app.post(
    "/predict",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "prediction": [45.3, 78.9]
                    }
                }
            },
            "description": "A list of predicted rental prices."
        }
    }
)
async def predict(
    car_features_list: List[CarFeatures] = Body(
        ...,
        example=[
            {
                "model_key": "Peugeot",
                "mileage": 15000.0,
                "engine_power": 120.0,
                "fuel": "diesel",
                "paint_color": "black",
                "car_type": "hatchback",
                "private_parking_available": True,
                "has_gps": True,
                "has_air_conditioning": True,
                "automatic_car": False,
                "has_getaround_connect": True,
                "has_speed_regulator": True,
                "winter_tires": False
            },
            {
                "model_key": "BMW",
                "mileage": 5000.0,
                "engine_power": 200.0,
                "fuel": "petrol",
                "paint_color": "blue",
                "car_type": "sedan",
                "private_parking_available": False,
                "has_gps": True,
                "has_air_conditioning": True,
                "automatic_car": True,
                "has_getaround_connect": False,
                "has_speed_regulator": True,
                "winter_tires": True
            }
        ]
    )
):
    """
    Predict the recommended rental price for one or more cars.
    
    ### Description
    This endpoint predicts the recommended rental price for one or more cars based on their features.
    
    ### Input
    - A list of car features (see the input example for details).
    
    ### Available Options for Input Fields:
    - **`model_key`**: The car's brand.  
      Options: `'Citroën'`, `'Peugeot'`, `'PGO'`, `'Renault'`, `'Audi'`, `'BMW'`, `'Ford'`, `'Mercedes'`, `'Opel'`, `'Porsche'`, `'Volkswagen'`, `'KIA Motors'`, `'Alfa Romeo'`, `'Ferrari'`, `'Fiat'`, `'Lamborghini'`, `'Maserati'`, `'Lexus'`, `'Honda'`, `'Mazda'`, `'Mini'`, `'Mitsubishi'`, `'Nissan'`, `'SEAT'`, `'Subaru'`, `'Suzuki'`, `'Toyota'`, `'Yamaha'`.
    
    - **`fuel`**: The type of fuel the car uses.  
      Options: `'diesel'`, `'petrol'`, `'hybrid_petrol'`, `'electro'`.
    
    - **`paint_color`**: The color of the car.  
      Options: `'black'`, `'grey'`, `'white'`, `'red'`, `'silver'`, `'blue'`, `'orange'`, `'beige'`, `'brown'`, `'green'`.
    
    - **`car_type`**: The type of car.  
      Options: `'convertible'`, `'coupe'`, `'estate'`, `'hatchback'`, `'sedan'`, `'subcompact'`, `'suv'`, `'van'`.
   
    
    ### Output
    - A dictionary containing the key `"prediction"` with a list of predicted rental prices.
    """
    try:
        # Convert the list of CarFeatures instances to a DataFrame
        X = pd.DataFrame([car_features.model_dump() for car_features in car_features_list])
        
        # Make predictions
        prediction = model.predict(X)
        
        # Return the predictions as a JSON-serializable response
        return {"prediction": prediction.tolist()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
