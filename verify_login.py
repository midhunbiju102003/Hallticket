import urllib.request
import json

def test_login(username, password, role):
    url = 'http://localhost:8000/api/login/'
    data = json.dumps({
        'username': username,
        'password': password,
        'role': role
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        print(f"SUCCESS: {result.get('success')}")
        print(f"User: {result.get('user')}")
        return True
    except Exception as e:
        error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        print(f"ERROR: {e.code if hasattr(e, 'code') else 'Unknown'} - {error_body}")
        return False

print("Testing Admin Login...")
test_login('admin', 'admin123', 'admin')

print("\nTesting Staff Login...")
test_login('staff', 'staff123', 'staff')
