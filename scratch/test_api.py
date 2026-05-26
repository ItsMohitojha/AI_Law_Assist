import urllib.request
import json
import ssl

try:
    req = urllib.request.Request(
        'http://localhost:5000/api/chat/stream',
        data=json.dumps({"question": "test", "session_id": "test"}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as response:
        print("Status:", response.status)
        print("Body:", response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code)
    print("Error Body:", e.read().decode('utf-8'))
except Exception as e:
    print("Other Error:", str(e))
