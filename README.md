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

## 📋 Features

### Backend
- ✅ SQLite database with SQLAlchemy ORM
- ✅ Campaign, Product, and Post models with relationships
- ✅ Database auto-initialization with sample data
- ✅ RESTful API endpoints for Campaigns, Products, and Posts
- ✅ Static file serving at `/static/` endpoint
- ✅ CORS configuration for frontend integration
- ✅ **AI-Powered Post Generation with Google Gemini 2.5**
  - Text generation (headline, body, caption, color)
  - Image generation and editing (img2img)
- ✅ **Image Compositing with PIL/Pillow**
  - HUGE stylized headlines with vibrant backgrounds
  - Neo-brutalist design (thick borders, high contrast)
  - Multiple aspect ratios (1:1, 16:9, 9:16)
- ✅ Comprehensive logging with emoji indicators

### Frontend
- ✅ React + Vite setup
- ✅ Tailwind CSS with Neo-Brutalist theme
- ✅ Dark/Light mode toggle with ThemeContext
- ✅ Campaign listing and management
- ✅ Product listing and management
- ✅ **Posts Page with AI Generation**
  - Instagram-style compact cards
  - Aspect ratio selector (Square, Landscape, Story)
  - Edit, Download, Delete actions
  - Real-time generation progress
- ✅ Responsive design across all pages

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
- **Google Generative AI (Gemini 2.5) 0.8.0+**
- **Pillow (PIL) 10.0.0+** - Image compositing
- **HTTPX 0.25.0+** - Async HTTP client

**Frontend:**
- React 18.2
- Vite 5.0 (build tool)
- Tailwind CSS 3.3
- React Router DOM (navigation)
- Context API (state management)

## 📊 Database Schema

### Campaign Table
- `id` (String/UUID, Primary Key)
- `name` (Text)
- `campaign_message` (Text)
- `call_to_action` (Text)
- `target_region` (Text)
- `target_audience` (Text)
- `brand_images` (Text/JSON)
- `created_at` (DateTime)

### Product Table
- `id` (String/UUID, Primary Key)
- `campaign_id` (Foreign Key → Campaign)
- `name` (Text)
- `description` (Text)
- `image_path` (Text)
- `created_at` (DateTime)

### Post Table (AI-Generated Content)
- `id` (String/UUID, Primary Key)
- `campaign_id` (Foreign Key → Campaign)
- `product_id` (Foreign Key → Product)
- `headline` (Text) - Short, punchy headline for image overlay
- `body_text` (Text) - Main post content (2-3 sentences)
- `caption` (Text) - Social media caption
- `text_color` (Text) - Hex color code for headline background
- `image_1_1` (Text) - Path to 1:1 aspect ratio image
- `image_16_9` (Text) - Path to 16:9 aspect ratio image
- `image_9_16` (Text) - Path to 9:16 aspect ratio image
- `generation_prompt` (Text) - User's prompt used for generation
- `created_at` (DateTime)

## 🔌 API Endpoints

### Campaigns
- `GET /api/campaigns` - List all campaigns
- `GET /api/campaigns/{id}` - Get single campaign
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/validate` - Validate campaign data
- `PUT /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign

### Products
- `GET /api/products?campaign_id={id}` - List products for campaign
- `GET /api/products/{id}` - Get single product
- `POST /api/products` - Create product
- `POST /api/products/validate` - Validate product data
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Posts (AI-Generated Content)
- `GET /api/posts?campaign_id={id}` - List posts for campaign
- `GET /api/posts/{id}` - Get single post
- `POST /api/posts/generate` - **AI generate post with Gemini**
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post

### Media
- `POST /api/media/upload` - Upload image files

### AI Post Generation Example

**Request:**
```json
POST /api/posts/generate
{
  "campaign_id": "uuid-string",
  "product_id": "uuid-string",
  "prompt": "Create a vibrant summer vibe post",
  "aspect_ratios": ["1:1", "16:9", "9:16"]
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "campaign_id": "uuid-string",
  "product_id": "uuid-string",
  "headline": "Summer Vibes Are Here",
  "body_text": "Get ready for the hottest season with our new collection...",
  "caption": "Tag a friend who needs this! #SummerVibes",
  "text_color": "#FF4081",
  "image_1_1": "posts/Campaign_Headline/image_1-1.png",
  "image_16_9": "posts/Campaign_Headline/image_16-9.png",
  "image_9_16": "posts/Campaign_Headline/image_9-16.png",
  "generation_prompt": "Create a vibrant summer vibe post",
  "created_at": "2025-01-30T12:00:00"
}
```

## 🔑 Gemini API Setup

To use the AI post generation feature, you need a Google Gemini API key:

1. **Get your API key:**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy your API key

2. **Add to environment variables:**
   ```bash
   cd backend
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Verify installation:**
   ```bash
   pip install google-generativeai>=0.8.0
   ```

**Models Used:**
- `gemini-2.5-flash` - Text generation (headline, body, caption, color)
- `gemini-2.5-flash-image` - Image generation and editing (img2img)

## 🎯 How It Works: AI Post Generation

### Two-Step Generation Process

1. **Text Generation (Gemini 2.5 Flash)**
   - Analyzes campaign message, target audience, and product details
   - Generates professional social media copy
   - Suggests vibrant hex color for headline background
   - Returns: `{headline, body_text, caption, text_color}`

2. **Image Generation & Compositing**
   - **Step 2a:** Gemini 2.5 Flash Image transforms product image
     - Applies campaign-appropriate styling and atmosphere
     - Keeps product recognizable while enhancing visual appeal
     - Uses img2img (image-to-image) generation

   - **Step 2b:** PIL compositor adds headline overlay
     - Uses Gemini-generated image as canvas
     - Adds HUGE stylized headline (120px, 100px, 140px fonts)
     - Vibrant colored background with thick black borders
     - Neo-brutalist aesthetic for maximum impact
     - Adds brand logo watermark

3. **Multiple Aspect Ratios**
   - 1:1 (1080x1080) - Instagram square
   - 16:9 (1920x1080) - Landscape/YouTube
   - 9:16 (1080x1920) - Story/Vertical

## 📝 Future Enhancements

- [ ] Edit post functionality (currently shows alert)
- [ ] Batch post generation
- [ ] Export posts as ZIP
- [ ] Post scheduling
- [ ] A/B testing different prompts
- [ ] Post performance tracking
- [ ] Regenerate individual aspect ratios

## 📄 License

This is a proof of concept project.
