
#!/usr/bin/env python3
import requests
import time
import sys

def check_service(name, url, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} is running at {url}")
            return True
        else:
            print(f"❌ {name} returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name} is not accessible: {e}")
        return False

def main():
    print("🔍 Checking AI Manus services...")
    
    services = [
        ("MockServer", "http://localhost:8090/health"),
        ("Sandbox", "http://localhost:8080/health"),
        ("Backend", "http://localhost:8000/api/v1/health"),
        ("Frontend", "http://localhost:5173")
    ]
    
    all_healthy = True
    for name, url in services:
        if not check_service(name, url):
            all_healthy = False
    
    if all_healthy:
        print("\n🎉 All services are running successfully!")
        print("You can now access AI Manus at: http://localhost:5173")
    else:
        print("\n⚠️  Some services are not running. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main()
