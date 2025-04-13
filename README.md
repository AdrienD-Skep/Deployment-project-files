# GetAround Analysis & Pricing Optimization
**Autheur** : [Adrien DOUCET](https://github.com/AdrienD-Skep)

**Application** : 

[dashboard](https://adriend-skep-Getaround-analysis-dashboard.hf.space)

[Api](https://adriend-skep-getaround-analysis-api.hf.space/docs)

This project addresses two key challenges for GetAround, the car rental platform:
1. **Data Analysis**: Determine optimal thresholds for rental delays to balance user satisfaction and revenue.
2. **Machine Learning**: Predict optimal car prices using a trained model accessible via API.

## 📖 Project Overview

### Context
Late car returns cause friction for subsequent rentals. GetAround aims to implement a minimum delay between rentals but needs data-driven insights to decide:
- **Threshold**: Minimum delay duration.
- **Scope**: Apply to all cars or only "Connect" cars.

### Goals
- Analyze historical delays to answer:
  - Share of revenue affected by the feature.
  - Number of impacted rentals per threshold/scope.
  - Frequency and impact of late checkins.
- Build a dashboard for visualization.
- Deploy a ML model API for price predictions.

### Example of API Usage

```python
from pydantic import BaseModel
import requests 
import json


class CarFeatures(BaseModel) :
    model_key                  :  str
    mileage                    :  float
    engine_power               :  float
    fuel                       :  str
    paint_color                :  str
    car_type                   :  str
    private_parking_available  :  bool
    has_gps                    :  bool
    has_air_conditioning       :  bool
    automatic_car              :  bool
    has_getaround_connect      :  bool
    has_speed_regulator        :  bool
    winter_tires               :  bool


car_1 = CarFeatures(
    model_key="Citroën", # The car's brand. Options: 'Citroën', 'Peugeot', 'PGO', 'Renault', 'Audi', 'BMW', 'Ford', 'Mercedes', 'Opel', 'Porsche', 'Volkswagen', 'KIA Motors', 'Alfa Romeo', 'Ferrari', 'Fiat', 'Lamborghini', 'Maserati', 'Lexus', 'Honda', 'Mazda', 'Mini', 'Mitsubishi', 'Nissan', 'SEAT', 'Subaru', 'Suzuki', 'Toyota', 'Yamaha'
    mileage=140411.0,
    engine_power=100.0,
    fuel="diesel", # The type of fuel the car uses. Options: 'diesel', 'petrol', 'hybrid_petrol', 'electro'.
    paint_color="black", # The color of the car. Options: 'black', 'grey', 'white', 'red', 'silver', 'blue', 'orange', 'beige', 'brown', 'green'.
    car_type="convertible", # The type of car. Options: 'convertible', 'coupe', 'estate', 'hatchback', 'sedan', 'subcompact', 'suv', 'van'
    private_parking_available=True,
    has_gps=True,
    has_air_conditioning=False,
    automatic_car=False,
    has_getaround_connect=True,
    has_speed_regulator=True,
    winter_tires=True
)

car_2 = CarFeatures(
    model_key="Peugeot",
    mileage=43662.0,
    engine_power=180.0,
    fuel="petrol",
    paint_color="orange",
    car_type="convertible",
    private_parking_available=True,
    has_gps=False,
    has_air_conditioning=False,
    automatic_car=False,
    has_getaround_connect=True,
    has_speed_regulator=False,
    winter_tires=True
)

car_features_list = [car_1, car_2]
r = requests.post(url="https://adriend-skep-getaround-analysis-api.hf.space/predict", json=[Car_features.model_dump() for Car_features in car_features_list])
r.json() # Output: {'prediction': [106.42868041992188, 134.3252716064453]}
```
