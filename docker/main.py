from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="Patient BMI Checker")


# This class defines what data we expect from the caller
class PatientData(BaseModel):
    name: str
    weight_kg: float
    height_cm: float


# This class defines what we send back to the caller
class BMIResult(BaseModel):
    name: str
    bmi: float
    category: str
    advice: str


# This endpoint runs when someone sends a POST request to /check-bmi
@app.post("/check-bmi", response_model=BMIResult)
def check_bmi(patient: PatientData):
    height_m = patient.height_cm / 100
    bmi = round(patient.weight_kg / (height_m ** 2), 2)


    if bmi < 18.5:
        category = "Underweight"
        advice = "Patient may need nutritional support. Refer to a dietitian."
    elif bmi < 25.0:
        category = "Normal"
        advice = "BMI is in the healthy range. No action needed."
    elif bmi < 30.0:
        category = "Overweight"
        advice = "Advise dietary changes and regular physical activity."
    else:
        category = "Obese"
        advice = "High risk. Recommend immediate medical consultation."


    return BMIResult(name=patient.name, bmi=bmi,
                    category=category, advice=advice)


# A simple check to confirm the app is running
@app.get("/")
def home():
    return {"message": "Patient BMI Checker is running."}
