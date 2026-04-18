# 🚀 Frontend Quick Start Guide

## Get the Manager Dashboard Running in 3 Minutes

---

## ✅ Prerequisites

1. **Backend API must be running** on http://localhost:8000
   ```bash
   # Start backend first (in main project directory)
   python -m uvicorn app.main:app --reload
   ```

2. **Python 3.10+** installed
3. **pip** package manager

---

## 🎯 Installation Steps

### Step 1: Navigate to Frontend
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- Streamlit (web framework)
- Plotly (interactive charts)
- Pandas (data processing)
- Requests (API communication)

### Step 3: Run the Dashboard

**Option A: Using run script (Windows)**
```cmd
run.bat
```

**Option B: Using run script (Mac/Linux)**
```bash
chmod +x run.sh
./run.sh
```

**Option C: Direct command**
```bash
streamlit run app.py
```

### Step 4: Access Dashboard
Open your browser: **http://localhost:8501**

---

## 🎨 Using the Dashboard

### Quick Test Flow

1. **Verify API Connection**
   - Check sidebar: Should show "✅ API Connected"

2. **Fill in Leave Request**
   - Employee ID: `E105`
   - Department: Select any (e.g., `ENG_BACKEND`)
   - Dates: Pick dates 7+ days in future
   - Reason: `"Family wedding"`

3. **Click "Analyze Leave Request"**

4. **Review Results**
   - See color-coded recommendation
   - Check confidence score
   - Read AI summary
   - View charts

---

## 📊 Dashboard Tabs

### Tab 1: New Leave Request ⭐
**Main analysis interface**

Features:
- Leave request form
- Simple/Advanced mode toggle
- Real-time analysis
- Visual recommendations
- Interactive charts
- Action buttons

### Tab 2: Team Overview
**Department statistics**

Shows:
- All departments
- Team sizes
- Comparison chart

### Tab 3: About
**System documentation**

Contains:
- Feature explanations
- Business rules
- Decision factors
- Version info

---

## 🎯 Test Scenarios

### Scenario 1: Normal Approval (Expected: ✅ APPROVE)
```
Employee: E105
Department: DATA_SCIENCE
Start: [7 days from today]
End: [9 days from today]
Reason: "Vacation"
Mode: Simple
```

### Scenario 2: Short Notice (Expected: ⚠️ REVIEW_REQUIRED)
```
Employee: E110
Department: QA
Start: [Tomorrow]
End: [Day after]
Reason: "Emergency"
Mode: Simple
```

### Scenario 3: Critical Capacity (Expected: ❌ SUGGEST_REJECTION)
```
Employee: E105
Department: ENG_BACKEND
Mode: Advanced
Team Size: 5
Add 3 team members on leave for same dates
Reason: "Vacation"
```

---

## 🎨 Visual Features

### Recommendation Colors
- 🟢 **Green**: STRONGLY APPROVE (Burnout risk)
- 🔵 **Blue**: APPROVE (Safe to approve)
- 🟡 **Yellow**: REVIEW REQUIRED (Manual review)
- 🔴 **Red**: SUGGEST REJECTION (Critical issues)

### Charts
1. **Confidence Gauge**: 0-100% semicircle gauge
2. **Team Capacity Bar**: Stacked bar chart
3. **Gantt Chart**: Timeline view (Advanced mode)

---

## 🔧 Troubleshooting

### Issue: "API Disconnected" in sidebar

**Solutions:**
1. Start backend:
   ```bash
   cd ..
   python -m uvicorn app.main:app --reload
   ```

2. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

3. Check API URL in `.streamlit/secrets.toml`

---

### Issue: "No departments available"

**Solutions:**
1. Generate mock data in backend:
   ```bash
   cd ..
   python -m app.mock_data
   ```

2. Restart backend

3. Refresh dashboard (press 'R' in browser)

---

### Issue: Charts not showing

**Solutions:**
1. Update dependencies:
   ```bash
   pip install --upgrade plotly streamlit
   ```

2. Clear Streamlit cache:
   - Press 'C' in dashboard
   - Or restart: Ctrl+C, then `streamlit run app.py`

3. Check browser console for errors (F12)

---

### Issue: Port 8501 already in use

**Solution:**
```bash
streamlit run app.py --server.port 8502
```
Then access at http://localhost:8502

---

## ⚙️ Configuration

### Change API URL

Edit `.streamlit/secrets.toml`:
```toml
API_BASE_URL = "http://your-server:8000"
```

### Change Port

```bash
streamlit run app.py --server.port 8080
```

### Change Theme

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF6B6B"  # Change this
backgroundColor = "#FFFFFF"
```

---

## 🎓 Tips & Tricks

### Keyboard Shortcuts
- **R**: Rerun app
- **C**: Clear cache
- **Ctrl+C**: Stop server

### Best Practices
1. **Always start backend first**
2. **Use Simple mode** for quick analysis
3. **Use Advanced mode** for testing specific scenarios
4. **Check API status** in sidebar before analyzing

### Performance
- First load: ~2-3 seconds
- Analysis: ~1-3 seconds (depends on backend)
- Re-runs: Instant (cached)

---

## 📱 Dashboard Features

### Interactive Elements
- ✅ Form validation
- ✅ Date pickers
- ✅ Real-time metrics
- ✅ Interactive charts
- ✅ Responsive layout
- ✅ Action buttons

### Visual Feedback
- ✅ Loading spinners
- ✅ Success/error messages
- ✅ Color-coded recommendations
- ✅ Progress indicators
- ✅ Tooltips

---

## 🚀 Next Steps

After getting the dashboard running:

1. **Test all scenarios** (listed above)
2. **Explore both modes** (Simple vs Advanced)
3. **Check Team Overview** tab
4. **Read About** tab for documentation
5. **Try action buttons** (Approve/Reject)

---

## 📦 What's Running

When everything is set up:

```
Port 8000 → Backend API (FastAPI)
Port 8501 → Frontend Dashboard (Streamlit)
```

Both must be running for the system to work!

---

## 🎉 Success Checklist

- [ ] Backend API running on port 8000
- [ ] Frontend dashboard running on port 8501
- [ ] Sidebar shows "✅ API Connected"
- [ ] Can see departments in dropdown
- [ ] Analysis returns results
- [ ] Charts display correctly
- [ ] Recommendation shows with color

---

## 📞 Need Help?

1. **Check backend logs** for API errors
2. **Check browser console** (F12) for frontend errors
3. **Verify all dependencies** installed: `pip list`
4. **Try the test scenarios** to verify functionality

---

## 💡 Pro Tips

### Quick Reset
```bash
# Stop both servers (Ctrl+C in each terminal)
# Restart backend
cd .. && python -m uvicorn app.main:app --reload

# In new terminal, restart frontend
cd frontend && streamlit run app.py
```

### View Logs
- **Backend**: Shows in terminal running uvicorn
- **Frontend**: Shows in terminal running streamlit
- **Browser**: F12 → Console tab

### Fast Development
1. Edit `app.py`
2. Save file
3. Streamlit auto-reloads!

---

**Happy Analyzing! 🎉**

*The dashboard provides a beautiful, intuitive interface for the AI-powered leave review system.*
