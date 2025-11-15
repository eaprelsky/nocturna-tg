"""Test script for Nocturna Chart Service"""

import requests
import base64
from datetime import datetime

# Service configuration
BASE_URL = "http://localhost:3011"
API_KEY = "66a435cf6ce9e96a3212f0772314f02459a64a5488fba277a2ac362230d755fb"

# Debug mode
DEBUG = True

def test_health():
    """Test health check endpoint"""
    print("🔍 Testing health check...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()
    return response.status_code == 200

def test_natal_chart():
    """Test natal chart rendering"""
    print("🎨 Testing natal chart rendering...")
    
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
        "renderOptions": {
            "format": "png",
            "width": 800,
            "height": 800
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Format: {data['data']['format']}")
            print(f"   Size: {data['data']['size']} bytes")
            print(f"   Dimensions: {data['data']['dimensions']['width']}x{data['data']['dimensions']['height']}")
            print(f"   Render time: {data['meta']['renderTime']}ms")
            
            # Save image
            image_base64 = data['data']['image']
            image_bytes = base64.b64decode(image_base64)
            
            filename = f"test_natal_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(filename, 'wb') as f:
                f.write(image_bytes)
            
            print(f"   💾 Image saved: {filename}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        print()

def test_transit_chart():
    """Test transit chart rendering"""
    print("🌟 Testing transit chart rendering...")
    
    url = f"{BASE_URL}/api/v1/chart/render/transit"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "natal": {
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
            ]
        },
        "transit": {
            "planets": {
                "sun": {"lon": 290.15, "lat": 0.0},
                "moon": {"lon": 45.67, "lat": 4.8},
                "mercury": {"lon": 275.30, "lat": -1.5},
                "venus": {"lon": 310.45, "lat": 2.1},
                "mars": {"lon": 180.20, "lat": -1.2},
                "jupiter": {"lon": 65.80, "lat": 0.8},
                "saturn": {"lon": 350.90, "lat": 2.5},
                "uranus": {"lon": 25.40, "lat": -0.5},
                "neptune": {"lon": 330.10, "lat": 1.0},
                "pluto": {"lon": 275.60, "lat": 16.2}
            },
            "datetime": datetime.now().isoformat()
        },
        "aspectSettings": {
            "natalToTransit": {
                "enabled": True,
                "orb": 3
            }
        },
        "renderOptions": {
            "format": "png",
            "width": 1000,
            "height": 1000
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success!")
            print(f"   Format: {data['data']['format']}")
            print(f"   Size: {data['data']['size']} bytes")
            print(f"   Render time: {data['meta']['renderTime']}ms")
            
            if 'chartInfo' in data['data']:
                chart_info = data['data']['chartInfo']
                if 'aspectsFound' in chart_info:
                    aspects = chart_info['aspectsFound']
                    print(f"   Aspects found: {aspects.get('natalToTransit', 0)} transit aspects")
            
            # Save image
            image_base64 = data['data']['image']
            image_bytes = base64.b64decode(image_base64)
            
            filename = f"test_transit_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            with open(filename, 'wb') as f:
                f.write(image_bytes)
            
            print(f"   💾 Image saved: {filename}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        print()

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Nocturna Chart Service Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health()))
    
    # Test 2: Natal Chart
    results.append(("Natal Chart", test_natal_chart()))
    
    # Test 3: Transit Chart (if endpoint exists)
    results.append(("Transit Chart", test_transit_chart()))
    
    # Summary
    print("=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {name}")
    print()
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    print(f"Total: {passed}/{total} tests passed")
    print("=" * 60)

if __name__ == "__main__":
    main()

