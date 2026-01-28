from crewai.tools import tool
from pydantic import BaseModel
from typing import Dict, Any
import joblib
import numpy as np
import pandas as pd

model_path = "../artifacts/model/model.pkl"
model = joblib.load(model_path)

@tool("predict_diabetes")
def predict_diabetes(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts the risk of diabetes based on patient health data.

    Parameters:
    - patient_data (Dict[str, Any]): A dictionary containing patient health metrics.

    Returns:
    - Dict[str, Any]: A dictionary containing the prediction result, probability, and test results.
    """
    # Convert input data to DataFrame
    input_df = pd.DataFrame([patient_data])

    # Ensure the input features are in the correct order
    feature_order = [
        "Pregnancies", "Glucose", "BloodPressure", "SkinThickness",
        "Insulin", "BMI", "DiabetesPedigreeFunction", "Age"
    ]
    input_df = input_df[feature_order]

    # Make prediction
    prediction = model.predict(input_df)[0]
    prediction_probability = round(model.predict_proba(input_df)[0][1], 2)

    result = "Diabetic" if prediction == 1 else "Non-Diabetic"

    return {
        "result": result,
        "probability": float(prediction_probability),
        "test_results": input_df.to_dict(orient="records")[0]
    }
