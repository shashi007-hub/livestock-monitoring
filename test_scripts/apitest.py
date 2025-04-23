import requests
import base64

BASE_URL = "http://localhost:8000"
image_path = "cat.jpg"

# Read image and encode as base64
with open(image_path, "rb") as img_file:
    image_base64 = base64.b64encode(img_file.read()).decode("utf-8")

bovine_data = {
    "name": "Daisy2",
    "weight": 500,
    "breed": "Ongole",  # match your BreedType enum
    "age": 89,
    "location": "Farm 42",
    "father_id": None,
    "owner_id": 3,
    "mother_id": None,
    "image_base64": image_base64  # 🔥 Send image here
}

response = requests.post(f"{BASE_URL}/bovines/", json=bovine_data)

print(response.status_code)
print(response.json())
