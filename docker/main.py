
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Patient BMI Checker")


class PatientData(BaseModel):
    name: str
    weight_kg: float
    height_cm: float


class BMIResult(BaseModel):
    name: str
    bmi: float
    category: str
    advice: str


@app.get("/")
def home():
    return {"message": "Patient BMI Checker is running."}


@app.post("/check-bmi", response_model=BMIResult)
def check_bmi(patient: PatientData):

    if patient.height_cm <= 0:
        raise HTTPException(
            status_code=400,
            detail="Height must be greater than zero."
        )

    if patient.weight_kg <= 0:
        raise HTTPException(
            status_code=400,
            detail="Weight must be greater than zero."
        )

    height_m = patient.height_cm / 100
    bmi = round(patient.weight_kg / (height_m ** 2), 2)

    if bmi < 18.5:
        category = "Underweight"
        advice = "Consider nutritional guidance from a healthcare professional."

    elif bmi < 25:
        category = "Normal"
        advice = "BMI is in the healthy range."

    elif bmi < 30:
        category = "Overweight"
        advice = "Consider balanced nutrition and regular physical activity."

    else:
        category = "Obese"
        advice = "Consider consulting a healthcare professional."

    return BMIResult(
        name=patient.name,
        bmi=bmi,
        category=category,
        advice=advice
    )
