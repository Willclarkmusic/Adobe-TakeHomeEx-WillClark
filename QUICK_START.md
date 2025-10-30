# 🚀 Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- Node.js 16+ and npm installed

## Step 1: Backend Setup (Terminal 1)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
venv\Scripts\Activate.ps1
# On Windows (CMD):
venv\Scripts\activate.bat
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI server
uvicorn main:app --reload
```

**Backend will start at:** `http://localhost:8000`
- API Documentation: http://localhost:8000/docs
- Test the API: http://localhost:8000/api/campaigns

## Step 2: Frontend Setup (Terminal 2)

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start the Vite dev server
npm run dev
```

**Frontend will start at:** `http://localhost:5173`

## ✅ Verification

1. **Backend Health Check:**
   - Visit: http://localhost:8000
   - Should see: `{"message": "Creative Automation Hub API is running", ...}`

2. **API Test:**
   - Visit: http://localhost:8000/api/campaigns
   - Should see: Array with at least one campaign object

3. **Frontend Test:**
   - Visit: http://localhost:5173
   - Should see: Creative Automation Hub interface with campaign selector
   - Try: Toggle dark/light theme button

## 🎯 What You Should See

### Backend Console Output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
🚀 Starting Creative Automation Hub API...
✅ Database tables created/verified
✅ Seeded initial campaign data
```

### Frontend Console Output:
```
VITE v5.0.8  ready in 350 ms
➜  Local:   http://localhost:5173/
```

## 🐛 Troubleshooting

### Backend Issues:
- **Port 8000 already in use:** Change port with `uvicorn main:app --reload --port 8001`
- **Module not found:** Ensure you activated the virtual environment
- **Database errors:** Delete `backend/app.db` and restart (will auto-regenerate)

### Frontend Issues:
- **Port 5173 already in use:** Vite will automatically prompt for a different port
- **API connection failed:** Ensure backend is running on port 8000
- **Module not found:** Run `npm install` again

## 🎨 Features to Explore

1. **Campaign Selection:** Use the dropdown to switch between campaigns
2. **Theme Toggle:** Click the DARK/LIGHT button in the top-right
3. **API Exploration:** Visit http://localhost:8000/docs for interactive API documentation

## 📝 Next Development Steps

The Phase 1 scaffold is complete! Ready for:
- Product management endpoints
- File upload functionality
- AI creative generation integration
- Post creation features
