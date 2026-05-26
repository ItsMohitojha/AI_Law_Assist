import urllib.request
import json

def test_endpoint(question):
    print(f"=== Sending Question: {question} ===")
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/chat',
            data=json.dumps({"question": question, "session_id": "test"}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("Response:", res_data.get("answer"))
    except Exception as e:
        print("Error:", str(e))
    print("=======================================\n")

if __name__ == "__main__":
    test_endpoint("hey")
    test_endpoint("who are you?")
    test_endpoint("What is Article 21 of the Indian Constitution?")
