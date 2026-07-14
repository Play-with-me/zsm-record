import time, urllib.request, json
success = False
end = time.time() + 180
print('Waiting for backend deploy...')
while time.time() < end:
    try:
        req = urllib.request.Request('https://zsm-record-backend.onrender.com/api/v1/shop/seed_manual', headers={'User-Agent': 'Mozilla/5.0'})
        urllib.request.urlopen(req, timeout=10)
        data = json.loads(urllib.request.urlopen('https://zsm-record-backend.onrender.com/api/v1/shop/items').read().decode())
        if any('base64' in i['metadata_value'] for i in data):
            print('Success! Base64 images are live.')
            success = True
            break
    except Exception as e:
        print(f"Waiting... {e}")
    time.sleep(5)
if not success:
    print('Timed out')
