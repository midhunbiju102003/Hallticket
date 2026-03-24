import urllib.request
import json

def test_student_login(roll_number):
    url = 'http://localhost:8000/api/student-login/'
    data = json.dumps({
        'roll_number': roll_number
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        print(f"SUCCESS: {result.get('success')}")
        print(f"Token: {result.get('token')[:20]}...")
        return result.get('token')
    except Exception as e:
        error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        print(f"ERROR: {error_body}")
        return None

print("Testing Student Login (CS101)...")
token = test_student_login('CS101')

if token:
    print("\nTesting Authenticated Request (List Hall Tickets)...")
    url = 'http://localhost:8000/api/hall-tickets/'
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    })
    try:
        response = urllib.request.urlopen(req)
        print(f"SUCCESS: Authenticated request worked!")
        print(response.read()[:100])
    except Exception as e:
        error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
        print(f"ERROR: {error_body}")
