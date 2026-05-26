import urllib.request
import json
import urllib.parse

def test_stream(question):
    print(f"=== Testing Streaming for: {question} ===")
    try:
        req = urllib.request.Request(
            'http://localhost:5000/api/chat/stream',
            data=json.dumps({"question": question, "session_id": "test_stream_session"}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        full_text = ""
        with urllib.request.urlopen(req) as response:
            for line in response:
                line_str = line.decode('utf-8').strip()
                if not line_str.startswith('data: '):
                    continue
                data = line_str[6:].strip()
                
                if data == '[DONE]':
                    print("\n[Stream finished]")
                    break
                elif data.startswith('[ERROR]'):
                    print("\n[Stream error]:", data)
                    break
                elif data:
                    # Decode chunk
                    word = urllib.parse.unquote(data)
                    full_text += word + ' '
                    print(word, end=' ', flush=True)
                    
        print("\n\n--- RECONSTRUCTED FULL TEXT ---")
        print(full_text)
        print("--------------------------------\n")
        
    except Exception as e:
        print("Error during streaming test:", str(e))

if __name__ == "__main__":
    # Test a legal query that we know is in the database to see the full RAG formatting
    test_stream("What is the penalty for driving without a license?")
