import uvicorn
import pandas as pd 
from pydantic import BaseModel, conlist
from typing import Literal, List, Union
from fastapi import FastAPI, File, UploadFile
import joblib
import numpy as np

description = """
Welcome to the Getaround pricing optimizer !  

## Machine Learning

This is a machine learning endpoint that predicts the price for one car rental. Here is the endpoint:  

* `/predict` which accepts this format :  

    { "model_key": string among this list : ['Citroën', 'Renault', 'BMW', 'Peugeot', 'Audi', 'Nissan', 'Mitsubishi', 'Mercedes', 'Volkswagen', 'Toyota', 'SEAT', 'Subaru', 'PGO', 'Opel', 'Ferrari', 'Maserati'],  
    "mileage": integer,  
    "engine_power": integer,  
    "fuel": string among this list : ['diesel', 'petrol', 'hybrid_petrol'],  
    "paint_color": string among this list : ['black', 'grey', 'blue', 'white', 'brown', 'silver', 'red', 'beige', 'green', 'orange'],  
    "car_type": string among this list : ['estate', 'sedan', 'suv', 'hatchback', 'subcompact', 'coupe', 'convertible', 'van'],  
    "private_parking_available": boolean,  
    "has_gps": boolean,  
    "has_air_conditioning": boolean,  
    "automatic_car": boolean,  
    "has_getaround_connect": boolean,  
    "has_speed_regulator": boolean,  
    "winter_tires": boolean }  

  If you want to know the prediction for some feature values that are not contained in the above lists, please put the value of the list that is the closest to yours.

"""

tags_metadata = [
    
    {
        "name": "Machine_Learning",
        "description": "Prediction Endpoint."
    }
]

app = FastAPI(
    title="🚗 Getaround pricing optimizer",
    description=description,
    version="0.1",
    openapi_tags=tags_metadata
)


class FormFeatures(BaseModel):
    model_key : Literal['Citroën', 'Renault', 'BMW', 'Peugeot', 'Audi', 'Nissan', 'Mitsubishi', 'Mercedes', 'Volkswagen', 'Toyota', 'SEAT', 'Subaru', 'PGO', 'Opel', 'Ferrari', 'Maserati'] = 'Citroën'
    mileage : int = 97097
    engine_power : int = 160
    fuel : Literal['diesel', 'petrol', 'hybrid_petrol'] = 'diesel'
    paint_color : Literal['black', 'grey', 'blue', 'white', 'brown', 'silver', 'red', 'beige', 'green', 'orange'] = 'grey'
    car_type : Literal['estate', 'sedan', 'suv', 'hatchback', 'subcompact', 'coupe', 'convertible', 'van'] = 'estate'
    private_parking_available : bool = False
    has_gps : bool = False
    has_air_conditioning : bool = True
    automatic_car : bool = True
    has_getaround_connect : bool = True
    has_speed_regulator : bool = True
    winter_tires : bool = True


@app.get("/")
async def index():

    message = "Hello world! If you want to know how to use the API, check out documentation at `/docs`"

    return message

@app.post("/predict", tags=["Machine_Learning"])
async def predict(formFeatures: FormFeatures):
    """
    Pricing optimization 
    """
    #Building dataframe to make predictions with the model

    features_list = ['model_key', 'mileage', 'engine_power', 'fuel', 'paint_color', 'car_type', 'private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car', 'has_getaround_connect', 'has_speed_regulator', 'winter_tires', 'mileage_inverse']
    features_values = [formFeatures.model_key, formFeatures.mileage, formFeatures.engine_power, formFeatures.fuel, formFeatures.paint_color, formFeatures.car_type, formFeatures.private_parking_available, formFeatures.has_gps, formFeatures.has_air_conditioning, formFeatures.automatic_car, formFeatures.has_getaround_connect, formFeatures.has_speed_regulator, formFeatures.winter_tires, 1/formFeatures.mileage]
    X_topredict = pd.DataFrame(np.array([features_values]), columns = features_list)
    
    list_bool = ['private_parking_available', 'has_gps', 'has_air_conditioning', 'automatic_car', 'has_getaround_connect', 'has_speed_regulator', 'winter_tires']
    for item in list_bool :
        X_topredict[item] = X_topredict[item].map({'True': True, 'False': False}) #need to force dtypes to bool in the dataframe columns, otherwise dtypes is object and the model does not recognize the data into the columns
    
    # Load model
    loaded_model = joblib.load('xgbregressor.joblib')
    
    #prediction
    prediction = loaded_model.predict(X_topredict)

    # Format response
    response = {"prediction": prediction.tolist()}

    return response


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=4000)