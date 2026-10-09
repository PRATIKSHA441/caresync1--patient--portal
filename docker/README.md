# Patient BMI Checker API

A REST API built using FastAPI to calculate Body Mass Index (BMI) based on patient weight and height.

## Features

* Calculate patient BMI
* Classify BMI into Underweight, Normal, Overweight, or Obese
* Validate patient input
* Automated testing using Pytest
* Docker containerization

## Technologies

* Python
* FastAPI
* Pydantic
* Pytest
* Docker

## Run with Docker

Build the Docker image:

```bash
docker build -t patient-bmi-api .
```

Run the container:

```bash
docker run -d --name patient-bmi-container -p 8000:8000 patient-bmi-api
```

## API Documentation

Open Swagger UI:

http://127.0.0.1:8000/docs

## Example Request

```json
{
  "name": "Anjali Patil",
  "weight_kg": 55,
  "height_cm": 158
}
```

## Run Automated Tests

```bash
python -m pytest test_bmi.py -v
```
