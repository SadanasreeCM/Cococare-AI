import requests
import io
from PIL import Image, ImageDraw

def run_tests():
    base_url = "http://127.0.0.1:8000"
    print("1. Testing Health Endpoint...")
    r = requests.get(f"{base_url}/api/health")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("\n2. Testing Initial Statistics...")
    r = requests.get(f"{base_url}/api/statistics")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("\n3. Generating Sample Test Image...")
    img = Image.new("RGB", (600, 400), color=(34, 139, 34))
    draw = ImageDraw.Draw(img)
    # Draw leaf spot simulation
    draw.ellipse([200, 150, 260, 210], fill=(139, 69, 19))
    draw.ellipse([350, 200, 420, 270], fill=(160, 82, 45))
    
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    print("\n4. Testing /api/detect Endpoint...")
    files = {"file": ("test_leaf.jpg", img_bytes.getvalue(), "image/jpeg")}
    r = requests.post(f"{base_url}/api/detect?confidence=0.3", files=files)
    print(r.status_code, r.json())
    assert r.status_code == 200
    det_res = r.json()
    det_id = det_res.get("detection_id")

    print("\n5. Testing /api/history...")
    r = requests.get(f"{base_url}/api/history")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print(f"\n6. Testing /api/history/{det_id}...")
    r = requests.get(f"{base_url}/api/history/{det_id}")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("\n7. Testing Farm API endpoints...")
    farm_payload = {
        "user_id": 1,
        "name": "Green Palm Sanctuary",
        "location": "Pollachi, Tamil Nadu",
        "land_area": 3.5,
        "land_unit": "acres",
        "soil_type": "loamy",
        "water_source": "Borewell",
        "irrigation_method": "Drip",
        "existing_trees": 180,
        "planting_date": "2021-06-15",
        "soil_test_info": "pH 6.5, good organic carbon"
    }
    r = requests.post(f"{base_url}/api/farm", json=farm_payload)
    print("Create Farm:", r.status_code, r.json())
    assert r.status_code == 200

    r = requests.get(f"{base_url}/api/farm/user/1")
    print("Get Farm:", r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["name"] == "Green Palm Sanctuary"

    print("\n8. Testing Phase 2 Operations Endpoints...")
    # Irrigation
    r_irr = requests.post(f"{base_url}/api/irrigation", json={
        "farm_id": 1,
        "date": "2026-09-27",
        "block_name": "North Block",
        "duration_or_quantity": "2 hours drip",
        "notes": "Morning irrigation cycle",
        "status": "COMPLETED",
        "frequency_days": 7
    })
    print("Log Irrigation:", r_irr.status_code, r_irr.json())
    assert r_irr.status_code == 200

    # Soil Test
    r_soil = requests.post(f"{base_url}/api/soil", json={
        "farm_id": 1,
        "date": "2026-09-27",
        "ph": 6.8,
        "nitrogen": 210.0,
        "phosphorus": 18.5,
        "potassium": 240.0,
        "organic_carbon": 0.85
    })
    print("Log Soil Test:", r_soil.status_code, r_soil.json())
    assert r_soil.status_code == 200

    # Soil Interpretation
    r_interp = requests.get(f"{base_url}/api/soil/interpretation?ph=6.8&n=210&p=18.5&k=240&oc=0.85")
    print("Soil Interpretation:", r_interp.status_code, r_interp.json()["ph"])
    assert r_interp.status_code == 200

    # Fertilizer Templates
    r_fert = requests.get(f"{base_url}/api/fertilizer/templates")
    print("Fertilizer Templates:", r_fert.status_code, list(r_fert.json().keys()))
    assert r_fert.status_code == 200

    # Calendar Task
    r_cal = requests.post(f"{base_url}/api/calendar", json={
        "farm_id": 1,
        "activity_type": "fertilizer",
        "title": "Apply Compost",
        "scheduled_date": "2026-10-05",
        "status": "PENDING"
    })
    print("Add Calendar Task:", r_cal.status_code, r_cal.json())
    assert r_cal.status_code == 200

    print("\n9. Testing Phase 3 Finance & Growth Endpoints...")
    # Expense creation & summary
    r_exp = requests.post(f"{base_url}/api/expenses", json={
        "farm_id": 1,
        "category": "Fertilizers & Nutrients",
        "amount": 4500.0,
        "date": "2026-09-27",
        "notes": "Organic compost 500kg"
    })
    print("Log Expense:", r_exp.status_code, r_exp.json())
    assert r_exp.status_code == 200

    r_exp_sum = requests.get(f"{base_url}/api/expenses/summary/farm/1")
    print("Expense Summary:", r_exp_sum.status_code, r_exp_sum.json()["total_investment"])
    assert r_exp_sum.status_code == 200
    assert r_exp_sum.json()["total_investment"] >= 4500.0

    # Block creation
    r_blk = requests.post(f"{base_url}/api/blocks", json={
        "farm_id": 1,
        "block_name": "East Plot WCT",
        "tree_count": 60,
        "variety": "West Coast Tall (WCT)",
        "planting_date": "2021-05-10",
        "status": "Active"
    })
    print("Create Block:", r_blk.status_code, r_blk.json())
    assert r_blk.status_code == 200
    blk_id = r_blk.json()["id"]

    # Growth observation
    r_growth = requests.post(f"{base_url}/api/growth", json={
        "block_id": blk_id,
        "date": "2026-09-27",
        "observation_notes": "Good crown symmetry, no frond yellowing observed.",
        "tree_height_m": 4.2,
        "yield_nuts_per_tree": 22.0
    })
    print("Log Growth Record:", r_growth.status_code, r_growth.json())
    assert r_growth.status_code == 200

    print("\n10. Testing Phase 4 Weather & Link Endpoints...")
    # Weather endpoint
    r_weather = requests.get(f"{base_url}/api/weather?location=Pollachi")
    print("Weather API:", r_weather.status_code, r_weather.json()["temperature"], r_weather.json()["condition"])
    assert r_weather.status_code == 200
    assert "temperature" in r_weather.json()

    # Link detection to block & notes
    r_link = requests.patch(f"{base_url}/api/history/{det_id}/link", json={
        "block_id": blk_id,
        "farmer_notes": "Tested south frond #3"
    })
    print("Link Detection to Block:", r_link.status_code, r_link.json())
    assert r_link.status_code == 200
    assert r_link.json()["block_id"] == blk_id

    # Chatbot with farm context
    r_chat = requests.post(f"{base_url}/api/chat", json={
        "message": "What is the recommended fertilizer timing for my farm?",
        "language": "en"
    })
    print("Chatbot Contextual Response:", r_chat.status_code, r_chat.text[:150])
    if r_chat.status_code == 200:
        print("Chatbot Reply:", r_chat.json().get("reply", "")[:100] + "...")


    print("\n11. Testing Final Statistics...")
    r = requests.get(f"{base_url}/api/statistics")
    print(r.status_code, r.json())
    assert r.status_code == 200

    print("\nSUCCESS: All Phase 1, Phase 2, Phase 3 & Phase 4 API tests passed successfully!")

if __name__ == "__main__":
    run_tests()

