
import requests
import json

BASE = "http://127.0.0.1:8000/auth/signup/"

def test_signup(role, email, extra={}):
    print(f"\n--- Testing {role} ---")
    data = {
        "email": email,
        "password": "password123",
        "full_name": f"Test {role}",
        "role": role
    }
    data.update(extra)
    try:
        res = requests.post(BASE, json=data)
        print(f"Status: {res.status_code}")
        try:
            print(f"Response: {res.json()}")
        except:
            print(f"Response (text): {res.text[:200]}...")
    except Exception as e:
        print(f"Exception: {e}")

# 1. Candidate (Should work now)
test_signup("candidate", "debug_cand_2@test.com")

# 2. HR (Empty company - suspected fail)
test_signup("hr", "debug_hr_2@test.com")

# 3. HR (With company)
test_signup("hr", "debug_hr_3@test.com", {"company": "TestCorp"})

# 4. Interviewer
test_signup("interviewer", "debug_int_2@test.com", {"company": "IntCorp"}) # Company should be ignored
