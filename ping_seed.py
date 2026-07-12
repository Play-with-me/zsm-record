import time
import urllib.request
import json

for _ in range(30):
    try:
        req = urllib.request.Request('https://zsm-record-backend.onrender.com/api/v1/shop/seed_manual', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode()
            print("Response:", body)
            if 'Seeded successfully' in body or 'status' in body:
                break
    except Exception as e:
        print("Waiting...", e)
    time.sleep(10)
