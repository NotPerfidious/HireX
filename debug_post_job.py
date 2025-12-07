
import requests
import json

BASE = "http://127.0.0.1:8000"

def debug_post_job():
    # 1. Login as HR
    login_url = f"{BASE}/auth/login/"
    # Using the same HR credentials I used for previous tests
    hr_creds = {"email": "debug_hr_2@test.com", "password": "password123"} 
    
    s = requests.Session()
    try:
        res = s.post(login_url, json=hr_creds)
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            return
        
        token = res.json().get('access')
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 2. Simulate Payload from PostJob.jsx
        payload = {
            "title": "Debug Job Title",
            "description": "Debug Description", 
            "is_active": True, 
            "skill_ids": [], # Empty for now, or I can add some if I fetch them first
            "deadline": "2025-12-31" 
        }
        
        print(f"Sending payload: {json.dumps(payload, indent=2)}")
        
        post_url = f"{BASE}/jobs/"
        res = s.post(post_url, json=payload, headers=headers)
        
        if res.status_code == 500:
            import re
            match = re.search(r'<pre class="exception_value">([^<]+)</pre>', res.text)
            if match:
                print(f"Server Error Exception: {match.group(1)}")
            else:
                # Fallback: look for typical h1/h2 error
                match2 = re.search(r'<h1>([^<]+)</h1>', res.text)
                if match2:
                    print(f"Server Error Header: {match2.group(1)}")
        
        print(f"Status Code: {res.status_code}")
                
    except Exception as e:
        print(f"Error: {e}")

debug_post_job()
