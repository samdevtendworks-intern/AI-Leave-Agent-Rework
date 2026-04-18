# API Testing Guide

## Testing the Leave Review Agent API

This guide provides examples for testing all endpoints using cURL, Python, and Postman.

---

## 1. Health Check

### cURL
```bash
curl http://localhost:8000/health
```

### Python
```python
import requests

response = requests.get("http://localhost:8000/health")
print(response.json())
```

### Expected Response
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gemini_configured": true
}
```

---

## 2. Analyze Leave Request (Full Context)

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-leave" \
  -H "Content-Type: application/json" \
  -d '{
    "request": {
      "emp_id": "E105",
      "start": "2026-02-20",
      "end": "2026-02-22",
      "reason": "Family wedding",
      "dept_id": "ENG_BACKEND"
    },
    "team_context": [
      {
        "emp_id": "E102",
        "start": "2026-02-20",
        "end": "2026-02-25"
      }
    ],
    "total_team_size": 5
  }'
```

### Python
```python
import requests
from datetime import date, timedelta

# Calculate future dates
today = date.today()
start_date = today + timedelta(days=5)
end_date = start_date + timedelta(days=2)

payload = {
    "request": {
        "emp_id": "E105",
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "reason": "Family wedding",
        "dept_id": "ENG_BACKEND"
    },
    "team_context": [],
    "total_team_size": 5
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave",
    json=payload
)

result = response.json()
print(f"Recommendation: {result['recommendation']}")
print(f"Confidence: {result['confidence_score']}")
print(f"Team Availability: {result['team_availability_percentage']}%")
print(f"AI Summary: {result['ai_summary']}")
```

---

## 3. Analyze Leave Request (Simple - Auto Context)

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-leave-simple" \
  -H "Content-Type: application/json" \
  -d '{
    "emp_id": "E105",
    "start": "2026-02-25",
    "end": "2026-02-27",
    "reason": "Medical emergency",
    "dept_id": "ENG_BACKEND"
  }'
```

### Python
```python
import requests
from datetime import date, timedelta

today = date.today()
start_date = today + timedelta(days=7)
end_date = start_date + timedelta(days=2)

payload = {
    "emp_id": "E105",
    "start": start_date.isoformat(),
    "end": end_date.isoformat(),
    "reason": "Medical emergency",
    "dept_id": "ENG_BACKEND"
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave-simple",
    json=payload
)

print(response.json())
```

---

## 4. Test Different Scenarios

### Scenario 1: Critical Capacity (Should suggest rejection)

```python
import requests
from datetime import date, timedelta

today = date.today()
start = today + timedelta(days=3)
end = start + timedelta(days=1)

# Create scenario where 3 out of 5 team members are already absent
payload = {
    "request": {
        "emp_id": "E105",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "reason": "Personal work",
        "dept_id": "ENG_BACKEND"
    },
    "team_context": [
        {"emp_id": "E101", "start": start.isoformat(), "end": end.isoformat()},
        {"emp_id": "E102", "start": start.isoformat(), "end": end.isoformat()},
        {"emp_id": "E103", "start": start.isoformat(), "end": end.isoformat()}
    ],
    "total_team_size": 5
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave",
    json=payload
)

result = response.json()
print(f"Recommendation: {result['recommendation']}")  # Expected: SUGGEST_REJECTION
print(f"Availability: {result['team_availability_percentage']}%")  # Expected: 20%
```

### Scenario 2: Burnout Risk (Should strongly approve)

This requires an employee with history showing no leave in 6+ months:

```python
# Using the simple endpoint with mock data
# Employee E100-E149 in mock data have various patterns
# Some are marked as "burnout_risk" pattern

payload = {
    "emp_id": "E105",  # Check mock data for burnout risk employees
    "start": "2026-03-01",
    "end": "2026-03-05",
    "reason": "Much needed vacation",
    "dept_id": "ENG_BACKEND"
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave-simple",
    json=payload
)

result = response.json()
# If E105 has burnout pattern in mock data, recommendation will be STRONGLY_APPROVE
```

### Scenario 3: Weekend Extension

```python
from datetime import date

# Monday Feb 16, 2026
monday = date(2026, 2, 16)

payload = {
    "emp_id": "E110",
    "start": monday.isoformat(),
    "end": (monday + timedelta(days=1)).isoformat(),
    "reason": "Personal",
    "dept_id": "DATA_SCIENCE"
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave-simple",
    json=payload
)

result = response.json()
# Should detect weekend extension pattern
weekend_factors = [f for f in result['factors'] if f['type'] == 'WEEKEND_EXTENSION']
print(f"Weekend extension detected: {len(weekend_factors) > 0}")
```

### Scenario 4: Short Notice

```python
# Leave starting tomorrow
tomorrow = date.today() + timedelta(days=1)

payload = {
    "emp_id": "E115",
    "start": tomorrow.isoformat(),
    "end": (tomorrow + timedelta(days=2)).isoformat(),
    "reason": "Urgent family matter",
    "dept_id": "QA"
}

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave-simple",
    json=payload
)

result = response.json()
# Should flag short notice
print(f"Days until leave: {result['days_until_leave']}")  # Expected: 1
```

---

## 5. Get Available Departments

### cURL
```bash
curl http://localhost:8000/api/v1/departments
```

### Python
```python
response = requests.get("http://localhost:8000/api/v1/departments")
departments = response.json()

print("Available Departments:")
for dept in departments['departments']:
    print(f"  - {dept['dept_id']}: {dept['team_size']} members")
```

---

## 6. Get Data Statistics

### cURL
```bash
curl http://localhost:8000/api/v1/statistics
```

### Python
```python
response = requests.get("http://localhost:8000/api/v1/statistics")
stats = response.json()

print(f"Departments: {stats['departments']}")
print(f"Employees: {stats['employees_with_history']}")
print(f"Total Leaves: {stats['total_approved_leaves']}")
```

---

## 7. Complete Test Suite Script

Save this as `test_api.py`:

```python
#!/usr/bin/env python3
"""
Complete API Test Suite
Tests all endpoints and scenarios
"""

import requests
from datetime import date, timedelta
from typing import Dict

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health check endpoint"""
    print("
🏥 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    print(f"   Status: {data['status']}")
    print(f"   Version: {data['version']}")
    print(f"   Gemini: {'✅' if data['gemini_configured'] else '❌'}")

def test_analyze_leave_full():
    """Test full leave analysis"""
    print("
📊 Testing Full Leave Analysis...")
    
    today = date.today()
    start = today + timedelta(days=5)
    end = start + timedelta(days=2)
    
    payload = {
        "request": {
            "emp_id": "E105",
            "start": start.isoformat(),
            "end": end.isoformat(),
            "reason": "Family wedding",
            "dept_id": "ENG_BACKEND"
        },
        "team_context": [],
        "total_team_size": 5
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/analyze-leave", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    print(f"   Recommendation: {result['recommendation']}")
    print(f"   Confidence: {result['confidence_score']}")
    print(f"   Availability: {result['team_availability_percentage']}%")
    print(f"   Factors: {len(result['factors'])}")

def test_analyze_leave_simple():
    """Test simplified leave analysis"""
    print("
📋 Testing Simple Leave Analysis...")
    
    today = date.today()
    start = today + timedelta(days=7)
    end = start + timedelta(days=2)
    
    payload = {
        "emp_id": "E105",
        "start": start.isoformat(),
        "end": end.isoformat(),
        "reason": "Medical emergency",
        "dept_id": "ENG_BACKEND"
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/analyze-leave-simple", json=payload)
    assert response.status_code == 200
    
    result = response.json()
    print(f"   Recommendation: {result['recommendation']}")
    print(f"   AI Summary: {result['ai_summary'][:100]}...")

def test_get_departments():
    """Test get departments endpoint"""
    print("
🏢 Testing Get Departments...")
    
    response = requests.get(f"{BASE_URL}/api/v1/departments")
    assert response.status_code == 200
    
    data = response.json()
    print(f"   Total Departments: {data['total']}")
    for dept in data['departments'][:3]:
        print(f"   - {dept['dept_id']}: {dept['team_size']} members")

def test_get_statistics():
    """Test statistics endpoint"""
    print("
📈 Testing Get Statistics...")
    
    response = requests.get(f"{BASE_URL}/api/v1/statistics")
    assert response.status_code == 200
    
    stats = response.json()
    print(f"   Departments: {stats['departments']}")
    print(f"   Employees: {stats['employees_with_history']}")
    print(f"   Approved Leaves: {stats['total_approved_leaves']}")

def main():
    """Run all tests"""
    print("="*60)
    print("🧪 Leave Agent API Test Suite")
    print("="*60)
    
    try:
        test_health_check()
        test_analyze_leave_full()
        test_analyze_leave_simple()
        test_get_departments()
        test_get_statistics()
        
        print("
" + "="*60)
        print("✅ All tests passed!")
        print("="*60)
        
    except AssertionError as e:
        print(f"
❌ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("
❌ Could not connect to API. Is the server running?")
        print("   Start server with: python -m uvicorn app.main:app")

if __name__ == "__main__":
    main()
```

Run it with:
```bash
python test_api.py
```

---

## Expected Response Times

- Health Check: < 50ms
- Analyze Leave (without AI): < 200ms
- Analyze Leave (with Gemini): < 3 seconds
- Get Departments: < 100ms
- Get Statistics: < 100ms

---

## Troubleshooting

### 1. API not responding
```bash
# Check if server is running
curl http://localhost:8000/health

# If not running, start it:
./run.sh
# Or:
uvicorn app.main:app --reload
```

### 2. Gemini API errors
```bash
# Check if API key is configured
curl http://localhost:8000/health | jq '.gemini_configured'

# Update .env file with your key
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### 3. Department not found
```bash
# Check available departments
curl http://localhost:8000/api/v1/departments

# Use one of the listed dept_ids
```

---

## Performance Testing

### Apache Bench
```bash
# Test 100 requests with concurrency of 10
ab -n 100 -c 10 -T 'application/json' \
  -p request.json \
  http://localhost:8000/api/v1/analyze-leave
```

### Python Load Test
```python
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def make_request():
    start = time.time()
    response = requests.get("http://localhost:8000/health")
    duration = time.time() - start
    return duration

# Run 100 concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    durations = list(executor.map(lambda _: make_request(), range(100)))

print(f"Average: {sum(durations)/len(durations):.3f}s")
print(f"Max: {max(durations):.3f}s")
print(f"Min: {min(durations):.3f}s")
```
