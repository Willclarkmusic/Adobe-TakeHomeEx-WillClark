# Creative Automation Hub - PoC (Phase 1)

A full-stack Creative Automation Pipeline proof of concept with FastAPI backend (SQLite + SQLAlchemy) and React frontend (Vite + Tailwind CSS).

## 🏗️ Project Structure

```
.
├── files/              # Binary media storage
│   ├── media/         # Brand/Product images
│   └── posts/         # Generated creatives
├── backend/           # FastAPI application
│   ├── app.db        # SQLite database (auto-generated)
│   ├── main.py       # Application entry point
│   ├── database.py   # Database configuration
│   ├── api/          # API routers
│   │   └── campaigns.py
│   ├── models/       # Data models
│   │   ├── orm.py    # SQLAlchemy ORM models
│   │   └── pydantic.py # Pydantic schemas
│   └── services/     # Business logic
└── frontend/         # React application
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── context/
    │   │   └── ThemeContext.jsx
    │   └── components/
    └── index.html
```

## 🚀 Quick Start

### Backend Setup

1. **Create a Python virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the FastAPI server:**
   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/`

### Frontend Setup

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server:**
   ```bash
   npm run dev
   ```

   The app will be available at `http://localhost:5173`

## 📋 Phase 1 Features

### Backend
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Campaign and Product models with relationships
- ✅ Database auto-initialization with sample data
- ✅ RESTful API endpoint: `GET /api/campaigns`
- ✅ Static file serving at `/static/` endpoint
- ✅ CORS configuration for frontend integration

### Frontend
- ✅ React + Vite setup
- ✅ Tailwind CSS with Neo-Brutalist theme
- ✅ Dark/Light mode toggle with ThemeContext
- ✅ Campaign listing and selection
- ✅ Campaign details display
- ✅ Responsive design

## 🎨 Design System

**Neo-Brutalist Aesthetic:**
- Sharp corners (no border-radius)
- Bold 4px borders
- High contrast colors
- Drop shadows for depth
- Monospace fonts
- Uppercase typography

## 🛠️ Tech Stack

**Backend:**
- FastAPI 0.104.1
- SQLAlchemy 2.0.23
- Pydantic 2.5.0
- SQLite (file-based database)
- Uvicorn (ASGI server)

**Frontend:**
- React 18.2
- Vite 5.0 (build tool)
- Tailwind CSS 3.3
- Context API (state management)

## 📊 Database Schema

### Campaign Table
- `id` (String/UUID, Primary Key)
- `campaign_message` (Text)
- `target_region` (Text)
- `target_audience` (Text)
- `brand_images` (Text/JSON)

### Product Table
- `id` (String/UUID, Primary Key)
- `campaign_id` (Foreign Key → Campaign)
- `name` (Text)
- `description` (Text)
- `image_path` (Text)

## 🔌 API Endpoints

### `GET /api/campaigns`
Returns all campaigns from the database.

**Response:**
```json
[
  {
    "id": "uuid-string",
    "campaign_message": "Launch our new eco-friendly product line...",
    "target_region": "North America",
    "target_audience": "Environmentally conscious millennials aged 25-40",
    "brand_images": "[\"/static/media/brand-logo.png\"]"
  }
]
```

## 📝 Next Steps (Future Phases)

- [ ] Product management endpoints
- [ ] Image upload functionality
- [ ] AI-powered creative generation
- [ ] Post creation and management
- [ ] Advanced campaign analytics

## 📄 License

This is a proof of concept project.
