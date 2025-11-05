# Creative Automation Hub - Full-Featured Platform

A complete full-stack Creative Automation Platform with AI-powered content generation, mood board creation, and social media scheduling. Built with FastAPI backend (SQLite + SQLAlchemy) and React frontend (Vite + Tailwind CSS).
[Google Slides Presentation](https://docs.google.com/presentation/d/1EP0X0cgXCdmBxwkHgkhmVmCbU-whhIaQbC3UEaeoV1U/edit?usp=sharing)

## 🏗️ Project Structure

```
.
├── files/                    # Binary media storage
│   ├── media/               # Brand/Product images
│   ├── posts/               # AI-generated post creatives
│   └── moods/               # Mood board images and videos
├── examples/                # Sample JSON files for batch import
│   └── Campora_assets/      # Sample product images
├── backend/                 # FastAPI application
│   ├── app.db              # SQLite database (auto-generated)
│   ├── main.py             # Application entry point
│   ├── database.py         # Database configuration
│   ├── .env                # Environment variables (API keys)
│   ├── api/                # API routers (6 routers)
│   │   ├── campaigns.py    # Campaign management
│   │   ├── products.py     # Product management + AI regeneration
│   │   ├── posts.py        # AI post generation
│   │   ├── media.py        # File uploads
│   │   ├── moods.py        # Mood board generation (images/videos)
│   │   └── deploy.py       # Social media scheduling (Ayrshare)
│   ├── models/             # Data models
│   │   ├── orm.py          # SQLAlchemy ORM models
│   │   └── pydantic.py     # Pydantic schemas
│   └── services/           # Business logic
│       ├── gemini_service.py    # Google Gemini AI integration
│       ├── image_compositor.py  # PIL image compositing
│       └── file_manager.py      # File handling utilities
└── frontend/               # React application
    ├── src/
    │   ├── App.jsx
    │   ├── main.jsx
    │   ├── context/
    │   │   └── ThemeContext.jsx
    │   ├── pages/          # Main page components
    │   │   ├── CampaignPage.jsx
    │   │   ├── PostsPage.jsx
    │   │   ├── MoodBoardPage.jsx
    │   │   └── DeployPage.jsx
    │   └── components/     # Reusable UI components
    └── index.html
```

## 🚀 Quick Start

### Backend Setup

1. **Configure environment variables:**
   ```bash
   cd backend
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```bash
   # Required: Google Gemini API Key for AI post generation
   GEMINI_API_KEY=your_gemini_api_key_here

   # OPTIONAL: Ayrshare API Key for social media posting
   # Note: Account will connect but scheduling and posting features not yet available
   AYRSHARE_API_KEY=your_ayrshare_api_key_here
   ```

   - Get Gemini API Key: [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Get Ayrshare API Key (Optional): [Ayrshare Dashboard](https://app.ayrshare.com/)

2. **Create a Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the FastAPI server:**
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

## ✨ Feature Overview

### 🎯 Core Features
1. **Campaign Management** - Create and manage marketing campaigns with brand assets
2. **Product Management** - Organize product catalogs with images and descriptions
3. **AI Post Generation** - Generate social media content with Gemini AI
4. **Mood Board Creation** - Design inspirational content with AI-generated images/videos
5. **Social Media Scheduling** - Schedule posts across platforms via Ayrshare
6. **Batch Data Import** - Load campaigns and products from JSON/YAML files

---

## 📋 Detailed Features

### Backend (FastAPI + SQLite)

#### Database & ORM
- ✅ SQLite database with SQLAlchemy ORM
- ✅ 5 primary tables: Campaigns, Products, Posts, MoodMedia, ScheduledPosts
- ✅ Database auto-initialization with sample data
- ✅ Support for nullable foreign keys (flexible post sources)
- ✅ JSON field storage for arrays (brand_images, source_images, platforms)

#### API Endpoints (40+ endpoints across 6 routers)
- ✅ **Campaigns API** - Full CRUD with validation and nested product creation
- ✅ **Products API** - Full CRUD with batch operations and AI image regeneration
- ✅ **Posts API** - AI generation with multi-source image support
- ✅ **Media API** - File uploads with URL download support
- ✅ **Moods API** - Image and video generation with Gemini/Veo
- ✅ **Deploy API** - Ayrshare integration for social media scheduling

#### AI Integration (Google Gemini)
- ✅ **Gemini 2.5 Flash** - Text generation (headlines, body copy, captions, colors)
- ✅ **Gemini 2.5 Flash Image** - Image transformation and composition (img2img)
- ✅ **Veo 3.1** - Video generation for mood boards (4-8 seconds)
- ✅ **Product Image Regeneration** - Generate product photos from text descriptions
- ✅ Smart generation strategy - Single image (img2img) vs Multiple images (composition)
- ✅ Random logo selection from brand assets

#### Image Processing (PIL/Pillow)
- ✅ Neo-brutalist design with thick borders (8px) and high contrast
- ✅ HUGE stylized headlines (120px-140px fonts) with vibrant backgrounds
- ✅ Smart text wrapping and positioning
- ✅ Brand logo watermarking
- ✅ Multiple aspect ratios: 1:1, 16:9, 9:16 (posts) + 3:4, 4:3 (moods)
- ✅ Image composition from multiple sources

#### File Management
- ✅ Static file serving at `/static/` endpoint
- ✅ Three-tier file path handling:
  - URLs (download to local storage)
  - Local paths (copy to /files/media/)
  - /static/ paths (already processed)
- ✅ UUID-based unique filenames
- ✅ Support for multiple image formats (JPG, PNG, WEBP, GIF, SVG)
- ✅ Preview serving from /examples/ directory

#### Validation & Data Import
- ✅ Pydantic schema validation for all API requests
- ✅ JSON/YAML batch upload support
- ✅ Partial validation with missing field detection
- ✅ Atomic transactions for batch operations
- ✅ Auto-switches to manual form entry when fields are missing

#### Logging & Monitoring
- ✅ Comprehensive logging with emoji indicators (🎨 🚀 ✅ ❌)
- ✅ Step-by-step progress tracking for AI generation
- ✅ Detailed error messages with context
- ✅ CORS configuration for frontend integration

---

### Frontend (React + Tailwind CSS)

#### Pages & Navigation
- ✅ **Campaign Page** - View campaign details, schedule, products
- ✅ **Posts Page** - Generate and manage social media posts
- ✅ **Mood Board Page** - Create inspirational images and videos
- ✅ **Deploy Page** - Schedule and track social media posts
- ✅ React Router navigation with active state indicators

#### Campaign Management
- ✅ Campaign dropdown selector with live filtering
- ✅ Create/Edit campaigns with validation
- ✅ Batch JSON/YAML upload with preview
- ✅ Brand image management (multiple logos)
- ✅ Schedule configuration (start date + duration)
- ✅ Product listing with inline edit/delete

#### Product Management
- ✅ Grid-based product cards with images
- ✅ Manual product creation with image upload
- ✅ Batch product import from JSON
- ✅ **AI Image Regeneration** - Generate missing/corrupted product images
- ✅ Image error detection with fallback UI
- ✅ Confirmation modal for regeneration
- ✅ Real-time generation progress with loading states

#### AI Post Generation
- ✅ Multi-source image selector (products OR mood board)
- ✅ Instagram-style compact post cards
- ✅ Aspect ratio selector (Square 1:1, Landscape 16:9, Story 9:16)
- ✅ Source images preview (shows composition strategy)
- ✅ Real-time generation progress (10-20 seconds)
- ✅ Edit, Download, Delete actions
- ✅ Display of text content (headline, body, caption)

#### Mood Board Features
- ✅ Masonry gallery layout (Pinterest-style)
- ✅ **Image Generation** - Create 1-5 images at different ratios
- ✅ **Video Generation** - Create 4-8 second cinematic videos with Veo
- ✅ Manual upload support (images and videos)
- ✅ Multi-image selector for source blending
- ✅ Video playback in modal
- ✅ Download and delete functionality

#### Social Media Deployment (Ayrshare)
- ✅ Connected accounts display (Instagram, Facebook, Twitter, etc.)
- ✅ Post scheduling with date/time picker
- ✅ Platform selection (multi-select)
- ✅ Immediate posting or scheduled posting
- ✅ Scheduled posts list with status tracking
- ✅ Campaign-based filtering

#### UI/UX Features
- ✅ **Neo-Brutalist Theme** - Sharp corners, bold borders, high contrast
- ✅ **Dark/Light Mode** - System-wide theme toggle
- ✅ **Responsive Design** - Mobile, tablet, desktop layouts
- ✅ **Loading States** - Spinners, progress messages, disabled states
- ✅ **Error Handling** - User-friendly error messages and alerts
- ✅ **Confirmation Modals** - Safety prompts for destructive actions
- ✅ **Form Validation** - Client-side validation with instant feedback
- ✅ **Tab Interfaces** - Manual entry vs Batch upload
- ✅ **Drag-and-Drop** - File upload areas with visual feedback

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
- `call_to_action` (Text, Optional)
- `target_region` (Text)
- `target_audience` (Text)
- `brand_images` (Text/JSON) - Array stored as JSON string
- `start_date` (Date, Optional)
- `duration` (Integer, Optional) - Campaign duration in days
- `created_at` (DateTime)

### Product Table
- `id` (String/UUID, Primary Key)
- `campaign_id` (Foreign Key → Campaign)
- `name` (Text)
- `description` (Text, Optional)
- `image_path` (Text, Optional)
- `created_at` (DateTime)

### Post Table (AI-Generated Content)
- `id` (String/UUID, Primary Key)
- `campaign_id` (Foreign Key → Campaign)
- `product_id` (Foreign Key → Product, **Nullable**)
- `mood_id` (Foreign Key → MoodMedia, **Nullable**)
- `source_images` (Text/JSON, Optional) - Array of source image paths
- `headline` (Text) - Short, punchy headline for image overlay
- `body_text` (Text) - Main post content (2-3 sentences)
- `caption` (Text) - Social media caption
- `text_color` (Text, Optional) - Hex color code for headline background
- `image_1_1` (Text, Optional) - Path to 1:1 aspect ratio image
- `image_16_9` (Text, Optional) - Path to 16:9 aspect ratio image
- `image_9_16` (Text, Optional) - Path to 9:16 aspect ratio image
- `generation_prompt` (Text, Optional) - User's prompt used for generation
- `created_at` (DateTime)

**Key Feature**: Both `product_id` and `mood_id` are nullable, allowing posts to be generated from products, mood board images, or any combination.

### MoodMedia Table (Mood Board Content)
- `id` (String/UUID, Primary Key)
- `campaign_id` (Foreign Key → Campaign)
- `file_path` (Text) - Relative path (e.g., "moods/Campaign_img_timestamp_1-1.png")
- `gcs_uri` (Text, Optional) - Google Cloud Storage URI (for Veo videos)
- `media_type` (Text) - "image" or "video"
- `is_generated` (Boolean) - True if AI-generated, False if uploaded
- `prompt` (Text, Optional) - User's generation prompt
- `source_images` (Text/JSON, Optional) - Array of source image paths used
- `aspect_ratio` (Text, Optional) - "1:1", "16:9", "9:16", etc.
- `generation_metadata` (Text/JSON, Optional) - Additional generation details
- `created_at` (DateTime)

### ScheduledPost Table (Social Media Scheduling)
- `id` (String/UUID, Primary Key)
- `post_id` (Foreign Key → Post)
- `campaign_id` (Foreign Key → Campaign)
- `schedule_type` (Text) - "immediate", "scheduled", or "recurring"
- `platforms` (Text/JSON) - Array of platform names (e.g., ["instagram", "facebook"])
- `schedule_time` (DateTime, Optional) - When to post (null for immediate)
- `recurring_config` (Text/JSON, Optional) - Recurring schedule configuration
- `ayrshare_post_id` (Text, Optional) - Ayrshare's post ID after scheduling
- `status` (Text) - "pending", "scheduled", "posted", "failed"
- `error_message` (Text, Optional) - Error details if failed
- `created_at` (DateTime)

**Total Tables**: 5 primary tables with flexible relationships

## 🔌 API Endpoints (40+ Endpoints)

### Campaigns API (8 endpoints)
- `GET /api/campaigns` - List all campaigns
- `GET /api/campaigns/{id}` - Get single campaign
- `POST /api/campaigns` - Create campaign
- `POST /api/campaigns/with-products` - Create campaign with nested products
- `POST /api/campaigns/validate` - Validate campaign data from JSON
- `PUT /api/campaigns/{id}` - Update campaign (partial update)
- `DELETE /api/campaigns/{id}` - Delete campaign
- `GET /api/campaigns/{campaign_id}/products` - List products for campaign

### Products API (9 endpoints)
- `GET /api/products` - List all products (optional campaign_id filter)
- `GET /api/products/{id}` - Get single product
- `POST /api/products` - Create single product
- `POST /api/products/batch` - Create multiple products (atomic transaction)
- `POST /api/products/validate` - Validate single product from JSON
- `POST /api/products/batch/validate` - Validate multiple products
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- **`POST /api/products/{id}/regenerate-image`** - **AI generate product photo**

### Posts API (6 endpoints)
- `GET /api/posts` - List all posts (optional campaign_id filter)
- `GET /api/posts/{id}` - Get single post
- **`GET /api/posts/available-images`** - Get products and mood images for selection
- **`POST /api/posts/generate`** - **AI generate post with Gemini**
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post

### Media API (1 endpoint)
- `POST /api/media/upload` - Upload image files (multipart/form-data)

### Moods API (7 endpoints)
- `GET /api/moods` - List all mood media (optional campaign_id filter)
- `GET /api/moods/{id}` - Get single mood media
- `GET /api/moods/available-images` - Get products and mood images for blending
- **`POST /api/moods/generate-image`** - **AI generate mood board images**
- **`POST /api/moods/generate-video`** - **AI generate mood board videos (Veo)**
- `POST /api/moods/upload` - Manual upload of mood media
- `DELETE /api/moods/{id}` - Delete mood media

### Deploy API (3 endpoints)
- `GET /api/deploy/profiles` - List connected Ayrshare social media accounts
- `POST /api/deploy/schedule` - Schedule post to social media platforms
- `GET /api/deploy/scheduled` - List scheduled posts (optional campaign_id filter)

**📚 Full API Documentation**: See [API.md](./API.md) for complete endpoint details with request/response examples.

### AI Post Generation Example (Multi-Source)

**Request:**
```json
POST /api/posts/generate
{
  "campaign_id": "uuid-string",
  "source_images": [
    "/static/media/product_waterbottle.jpg",
    "moods/Summer_img_20250130_120000_1-1.png"
  ],
  "prompt": "Create a vibrant summer vibe post showcasing eco-friendly lifestyle",
  "aspect_ratios": ["1:1", "16:9", "9:16"]
}
```

**Response:**
```json
{
  "id": "uuid-string",
  "campaign_id": "uuid-string",
  "product_id": "uuid-string",
  "mood_id": "uuid-string",
  "source_images": "[\"media/product_waterbottle.jpg\", \"moods/Summer_img_20250130_120000_1-1.png\"]",
  "headline": "Summer Vibes Are Here",
  "body_text": "Get ready for the hottest season with our eco-friendly collection...",
  "caption": "Tag a friend who needs this! #SummerVibes #EcoFriendly",
  "text_color": "#FF4081",
  "image_1_1": "posts/Campaign_Headline/image_1-1.png",
  "image_16_9": "posts/Campaign_Headline/image_16-9.png",
  "image_9_16": "posts/Campaign_Headline/image_9-16.png",
  "generation_prompt": "Create a vibrant summer vibe post showcasing eco-friendly lifestyle",
  "created_at": "2025-01-30T12:00:00"
}
```


## 🎯 How It Works

### AI Post Generation (Multi-Source)

**Step 1: Text Generation** (Gemini 2.5 Flash)
- Analyzes campaign message, target audience, and available data (products/moods)
- Generates professional social media copy
- Suggests vibrant hex color for headline background
- Output: `{headline, body_text, caption, text_color}`

**Step 2: Image Strategy Selection**
- **Single Source Image** → img2img transformation
  - Uses Gemini 2.5 Flash Image to transform the image
  - Applies campaign-appropriate styling and atmosphere
  - Keeps subject recognizable while enhancing visual appeal

- **Multiple Source Images** → Composition/Blend
  - Uses Gemini 2.5 Flash Image to blend multiple images
  - Creates cohesive composition from products and mood references
  - Maintains brand consistency across sources

**Step 3: PIL Compositing**
- Uses Gemini-generated image as canvas
- Randomly selects one brand logo from campaign assets
- Adds HUGE stylized headline (120px-140px fonts)
- Vibrant colored background with thick black borders (8px)
- Neo-brutalist aesthetic for maximum social media impact
- Adds brand logo watermark to corner

**Step 4: Multi-Ratio Generation**
- Generates 1-3 aspect ratios per post:
  - 1:1 (1080x1080) - Instagram square
  - 16:9 (1920x1080) - Landscape/YouTube
  - 9:16 (1080x1920) - Story/Vertical
- Saves to structured path: `posts/{CampaignName}_{Headline}/image_{ratio}.png`

---

### Product Image Regeneration

When product images are missing or corrupted, the system can generate new product photos:

**Step 1: Create Base Template**
- Generates neutral 1080x1080 gray canvas

**Step 2: AI Transformation** (Gemini 2.5 Flash Image)
- Uses img2img to transform gray template into professional product photo
- Input: Product name + description + optional style prompt
- Output: Photorealistic product image suitable for e-commerce

**Step 3: Save & Update**
- Saves to `/files/media/product_{name}_{uuid}.png`
- Updates database with new image_path
- UI automatically refreshes to show new image

**Generation Time**: ~10-20 seconds

**Use Cases**: Unreadable formats (AVIF, HEIC), missing files, quick prototyping

---

### Mood Board Generation

**Image Generation:**
- Creates 1-5 separate images at different aspect ratios
- Can blend multiple source images for inspiration
- Pure visual content (no text overlays)
- Ratios: 1:1, 3:4, 4:3, 9:16, 16:9

**Video Generation (Veo 3.1):**
- Generates 4-8 second cinematic videos
- Supports 1 reference image for style guidance
- Smooth, professional motion
- Ratios: 16:9 (horizontal), 9:16 (vertical)
- Generation Time: ~30-60 seconds

## 🚧 Known Limitations

- **Gemini Flash Image**: Only supports img2img transformation (not pure text-to-image)
- **Veo Reference Images**: Maximum 1 reference image per video
- **Ayrshare Features**: Account connection works, but full scheduling UI is not yet production-ready
- **Post Editing**: Edit functionality currently shows alert (planned for future release)

---

## 📝 Future Enhancements

### Planned Features
- [ ] Full post editing modal (text + image regeneration)
- [ ] Batch post generation from product catalog
- [ ] Export posts as ZIP archive
- [ ] A/B testing with multiple prompt variations
- [ ] Post performance tracking and analytics
- [ ] Regenerate individual aspect ratios (keep others)
- [ ] Post templates library
- [ ] Advanced scheduling (recurring posts, post queues)
- [ ] Multi-language support for international campaigns

### Potential Integrations
- [ ] Additional social platforms (TikTok, LinkedIn, Pinterest)
- [ ] Cloud storage (AWS S3, Google Cloud Storage)
- [ ] Analytics dashboards (GA4, Mixpanel)
- [ ] CRM integration (HubSpot, Salesforce)

---

## 📚 Documentation

- **[API.md](./API.md)** - Complete API reference with 40+ endpoints
- **[QUICK_START.md](./QUICK_START.md)** - Step-by-step setup guide
- **[CLAUDE.md](./CLAUDE.md)** - Technical specifications for development

---

## 🎓 Key Learnings & Technical Highlights

### Architecture Decisions
- **Nullable Foreign Keys**: Flexible post sources (products OR mood board OR both)
- **JSON in TEXT Fields**: Storing arrays without complex migrations
- **Three-Tier File Paths**: URLs, local paths, and /static/ paths handled uniformly
- **Atomic Transactions**: Batch operations succeed or fail together
- **img2img Strategy**: Working within Gemini's capabilities (no text-to-image)

### AI Integration Patterns
- **Random Selection**: Logo randomization for visual variety
- **Smart Strategy**: Single vs multi-image generation logic
- **Progressive Enhancement**: Base template → AI transformation → PIL compositing
- **Error Resilience**: Graceful fallbacks when generation fails

### Frontend Patterns
- **Component Reusability**: MoodPopup used for multiple selection contexts
- **State Management**: Sets for tracking failed images and regeneration status
- **Optimistic UI**: Loading states and progress indicators
- **Form Flexibility**: Tab-based manual entry vs batch upload

---

## 📄 License

This is a proof of concept project for demonstration purposes.

---

*Last Updated: January 2025*
*Built with ❤️ using FastAPI, React, Google Gemini, and Veo*
