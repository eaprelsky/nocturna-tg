"""Simple single chart test"""

import requests
import base64
import time

BASE_URL = "http://localhost:3011"
API_KEY = "66a435cf6ce9e96a3212f0772314f02459a64a5488fba277a2ac362230d755fb"

url = f"{BASE_URL}/api/v1/chart/render"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "planets": {
        "sun": {"lon": 85.83, "lat": 0.0},
        "moon": {"lon": 133.21, "lat": 5.12},
        "mercury": {"lon": 95.45, "lat": -2.3},
        "venus": {"lon": 110.20, "lat": 1.5},
        "mars": {"lon": 45.30, "lat": -0.8},
        "jupiter": {"lon": 200.15, "lat": 0.5},
        "saturn": {"lon": 290.45, "lat": 2.1},
        "uranus": {"lon": 15.60, "lat": -0.3},
        "neptune": {"lon": 325.80, "lat": 1.2},
        "pluto": {"lon": 270.25, "lat": 15.0}
    },
    "houses": [
        {"lon": 300.32}, {"lon": 330.15}, {"lon": 355.24},
        {"lon": 20.32}, {"lon": 45.15}, {"lon": 75.24},
        {"lon": 120.32}, {"lon": 150.15}, {"lon": 175.24},
        {"lon": 200.32}, {"lon": 225.15}, {"lon": 255.24}
    ],
    # Note: PNG format does not support "quality" parameter in Puppeteer/Playwright
    # Only JPEG format supports "quality" (1-100)
    # If server adds "quality" by default for PNG, it's a server-side bug
    "renderOptions": {
        "format": "png",
        "width": 400,
        "height": 400
    }
}

print("🎨 Testing natal chart rendering...")
print(f"URL: {url}")
print(f"API Key: {API_KEY[:20]}...")
print(f"Sending request with 60s timeout...")
print()

start_time = time.time()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=60)
    elapsed = time.time() - start_time
    
    print(f"✅ Response received in {elapsed:.2f}s")
    print(f"Status code: {response.status_code}")
    print()
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success!")
        print(f"Format: {data['data']['format']}")
        print(f"Size: {data['data']['size']} bytes")
        print(f"Dimensions: {data['data']['dimensions']}")
        print(f"Render time: {data['meta']['renderTime']}ms")
        
        # Save image
        image_base64 = data['data']['image']
        image_bytes = base64.b64decode(image_base64)
        
        with open('test_chart.png', 'wb') as f:
            f.write(image_bytes)
        
        print(f"💾 Image saved: test_chart.png")
    else:
        print(f"❌ Error {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
except requests.exceptions.Timeout:
    elapsed = time.time() - start_time
    print(f"❌ Request timeout after {elapsed:.2f}s")
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

