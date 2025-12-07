
import requests
import json

BASE = "http://127.0.0.1:8000/jobs/applications/"

# Need to login as HR first to get a token?
# Or I can just check the view code (I already did) and rely on it.
# But running a script is better verification.

def debug_hr_data():
    # 1. Login as HR
    login_url = "http://127.0.0.1:8000/auth/login/"
    hr_creds = {"email": "debug_hr_2@test.com", "password": "password123"} 
    
    # Prerequisite: Ensure this user exists (created in previous debug step)
    
    s = requests.Session()
    try:
        res = s.post(login_url, json=hr_creds)
        if res.status_code != 200:
            print(f"Login failed: {res.text}")
            return
        
        token = res.json().get('access')
        headers = {'Authorization': f'Bearer {token}'}
        
        # 2. Fetch Applications
        res = s.get(BASE, headers=headers)
        if res.status_code != 200:
            print(f"Fetch failed: {res.text}")
            return
            
        data = res.json()
        print(f"Found {len(data)} applications.")
        
        for app in data:
            print(f"\nApplication ID: {app['id']}, Candidate: {app['applied_by']}")
            if 'interviews' in app:
                print(f"  - Interviews: {len(app['interviews'])}")
                for iv in app['interviews']:
                    print(f"    * ID: {iv['id']}, Date: {iv['date']}, Feedback: {iv.get('feedback')}")
            else:
                print("  - 'interviews' field MISSING in serializer output!")
                
    except Exception as e:
        print(f"Error: {e}")

debug_hr_data()
