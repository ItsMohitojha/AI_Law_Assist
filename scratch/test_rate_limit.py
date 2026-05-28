import urllib.request
import json
import time

url = 'http://localhost:5000/api/chat/stream'
data = json.dumps({"question": "What is the law?", "session_id": "test"}).encode('utf-8')
headers = {'Content-Type': 'application/json'}

print("Sending 6 requests to test rate limit...")

for i in range(6):
    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req) as response:
            print(f"Request {i+1}: Status {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Request {i+1}: Error Status {e.code}")
        print(f"Response Body: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Request {i+1}: Other Error: {e}")
