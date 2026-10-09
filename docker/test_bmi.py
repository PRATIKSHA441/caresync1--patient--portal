
import requests

URL = "http://127.0.0.1:8000/check-bmi"


def test_valid_bmi():
    patient = {
        "name": "Anjali Patil",
        "weight_kg": 55,
        "height_cm": 158
    }

    response = requests.post(URL, json=patient)

    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Anjali Patil"
    assert data["category"] == "Normal"
    assert data["bmi"] == 22.03


def test_invalid_height():
    patient = {
        "name": "Anjali Patil",
        "weight_kg": 55,
        "height_cm": 0
    }

    response = requests.post(URL, json=patient)

    assert response.status_code == 400

