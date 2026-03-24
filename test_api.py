import urllib.request
import json
url = 'http://localhost:8000/api/student-login/'
data = json.dumps({'roll_number': '123'}).encode('utf-8')
req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
try:
    response = urllib.request.urlopen(req)
    print("SUCCESS", response.read())
except Exception as e:
    print("ERROR", e.read() if hasattr(e, 'read') else str(e))
