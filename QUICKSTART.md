# 🚀 Quick Start Guide

## AI-Assisted Leave Review Agent - Get Running in 5 Minutes

---

## Prerequisites

You need:
- Python 3.10 or higher
- pip (Python package manager)
- Terminal/Command prompt

Optional:
- Docker (for containerized deployment)
- Google Gemini API key (for AI features)

---

## Option 1: Quick Start (Recommended)

### Step 1: Navigate to Project
```bash
cd leave-agent-backend
```

### Step 2: Run the Setup Script
```bash
chmod +x run.sh
./run.sh
```

That's it! The script will:
- ✅ Create virtual environment
- ✅ Install dependencies
- ✅ Generate mock data
- ✅ Start the server

### Step 3: Test the API
Open your browser: http://localhost:8000/docs

---

## Option 2: Manual Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Generate Mock Data
```bash
python -m app.mock_data
```

### Step 3: Configure (Optional)
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Step 4: Start Server
```bash
uvicorn app.main:app --reload
```

### Step 5: Access API
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## Option 3: Docker (Production)

### Step 1: Build and Run
```bash
docker-compose up -d
```

### Step 2: Check Status
```bash
docker-compose ps
docker-compose logs -f
```

### Step 3: Access
http://localhost:8000/docs

---

## Testing Your Installation

### 1. Health Check
```bash
curl http://localhost:8000/health
```

Expected output:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "gemini_configured": false
}
```

### 2. Quick Analysis Test
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-leave-simple" \
  -H "Content-Type: application/json" \
  -d '{
    "emp_id": "E105",
    "start": "2026-03-01",
    "end": "2026-03-03",
    "reason": "Family wedding",
    "dept_id": "ENG_BACKEND"
  }'
```

You should see a JSON response with:
- `recommendation`: One of STRONGLY_APPROVE, APPROVE, REVIEW_REQUIRED, SUGGEST_REJECTION
- `confidence_score`: Between 0 and 1
- `ai_summary`: Brief explanation
- `factors`: List of considerations

### 3. Interactive Testing
Visit http://localhost:8000/docs and use the interactive interface to test all endpoints.

---

## Common Issues & Solutions

### Issue 1: Port 8000 already in use
```bash
# Use a different port
uvicorn app.main:app --port 8080
```

### Issue 2: Python version error
```bash
# Check Python version (must be 3.10+)
python3 --version

# Use python3 explicitly
python3 -m uvicorn app.main:app
```

### Issue 3: Module not found
```bash
# Make sure you're in the project directory
cd leave-agent-backend

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue 4: Mock data not found
```bash
# Generate mock data manually
python -m app.mock_data
```

---

## Next Steps

### 1. Explore the API
Visit http://localhost:8000/docs to see all available endpoints

### 2. Run Tests
```bash
pytest tests/ -v
```

### 3. Read Documentation
- `README.md` - Complete project guide
- `docs/API_TESTING_GUIDE.md` - Testing examples
- `PROJECT_COMPLETION.md` - Implementation details

### 4. Configure Gemini AI (Optional)
```bash
# Edit .env file
nano .env

# Add your API key
GEMINI_API_KEY=your_key_here

# Restart server
# The AI summaries will now be enhanced
```

---

## File Structure Overview

```
leave-agent-backend/
├── app/                    # Main application code
│   ├── main.py            # FastAPI app (START HERE)
│   ├── models.py          # Data models
│   ├── analysis_engine.py # Core logic
│   ├── rules_engine.py    # Business rules
│   └── ai_service.py      # AI integration
│
├── tests/                 # Test suite
│   ├── test_analysis_engine.py
│   └── test_rules_engine.py
│
├── data/                  # Mock data (auto-generated)
│   ├── team_schedules.json
│   └── employee_histories.json
│
├── docs/                  # Documentation
│   └── API_TESTING_GUIDE.md
│
├── README.md              # Main documentation
├── PROJECT_COMPLETION.md  # Implementation summary
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── docker-compose.yml    # Orchestration
└── run.sh               # Quick start script
```

---

## Key Endpoints Reference

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Check system status |
| POST | `/api/v1/analyze-leave` | Analyze with full context |
| POST | `/api/v1/analyze-leave-simple` | Analyze with auto-context |
| GET | `/api/v1/departments` | List departments |
| GET | `/api/v1/statistics` | Get data stats |

---

## Example Requests

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/analyze-leave-simple",
    json={
        "emp_id": "E105",
        "start": "2026-03-01",
        "end": "2026-03-03",
        "reason": "Family wedding",
        "dept_id": "ENG_BACKEND"
    }
)

result = response.json()
print(f"Recommendation: {result['recommendation']}")
```

### cURL
```bash
curl -X POST "http://localhost:8000/api/v1/analyze-leave-simple" \
  -H "Content-Type: application/json" \
  -d '{"emp_id":"E105","start":"2026-03-01","end":"2026-03-03","reason":"Family wedding","dept_id":"ENG_BACKEND"}'
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/api/v1/analyze-leave-simple', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    emp_id: 'E105',
    start: '2026-03-01',
    end: '2026-03-03',
    reason: 'Family wedding',
    dept_id: 'ENG_BACKEND'
  })
});

const result = await response.json();
console.log('Recommendation:', result.recommendation);
```

---

## Performance Expectations

- Health check: **< 100ms**
- Analysis (without AI): **< 300ms**
- Analysis (with Gemini): **< 3 seconds**
- Concurrent requests: **100+ req/s**

---

## Support & Resources

### Documentation
- 📘 README.md - Full project guide
- 📗 API_TESTING_GUIDE.md - Testing examples
- 📙 PROJECT_COMPLETION.md - Implementation details

### Interactive
- 🌐 http://localhost:8000/docs - Swagger UI
- 🌐 http://localhost:8000/redoc - ReDoc UI

### Testing
- 🧪 `pytest tests/ -v` - Run test suite
- 🔍 `pytest tests/ --cov=app` - With coverage

---

## Success Checklist

- [ ] Server starts without errors
- [ ] Health endpoint returns 200
- [ ] Can access /docs in browser
- [ ] Simple analysis request works
- [ ] Mock data files exist in data/
- [ ] Tests pass with `pytest tests/ -v`

---

## Need Help?

1. **Check the logs**: Look for error messages in terminal
2. **Read README.md**: Comprehensive troubleshooting section
3. **Run tests**: `pytest tests/ -v` to verify functionality
4. **Check data**: Ensure `data/*.json` files exist

---

## What's Next?

After getting the system running, you can:

1. **Integrate with Core HRMS**: Replace mock data with database
2. **Add Frontend**: Build Streamlit dashboard for visualization
3. **Deploy to Production**: Use Docker in cloud environment
4. **Enhance AI**: Fine-tune prompts for better recommendations
5. **Add Features**: Implement additional business rules

---

**Ready to deploy?** See `README.md` for deployment guide.

**Want to contribute?** See `PROJECT_COMPLETION.md` for architecture details.

---

*Happy Coding! 🚀*
