# 🏛️ FDE Creative Automation Hub: Technical Specification (SQLite Edition)

## Overview

This project is a Proof of Concept (PoC) for a Creative Automation Pipeline. It consists of a **FastAPI** backend for data management (using SQLite/SQLAlchemy), file handling, and GenAI integration, and a **React + Tailwind CSS** frontend.

## 1. Directory Structure

/
├── files/ (For binary media files only)
│ ├── media/ (Uploaded Brand/Product Images)
│ ├── posts/ (Generated Post Creatives)
│ │ └── <CampaignID>/
├── backend/
│ ├── app.db (The SQLite database file)
│ ├── main.py (FastAPI entry, includes StaticFiles mount)
│ ├── .env (Environment variables - GEMINI_API_KEY)
│ ├── api/
│ │ ├── campaigns.py (Router)
│ │ ├── products.py (Router)
│ │ └── posts.py (Router - AI Post Generation)
│ ├── services/
│ │ ├── file_manager.py
│ │ ├── gemini_service.py (Google Gemini 2.5 Integration)
│ │ └── image_compositor.py (PIL Image Compositing)
│ ├── models/
│ │ ├── orm.py (SQLAlchemy ORM Models)
│ │ └── pydantic.py (Pydantic Schemas for API I/O)
│ └── database.py (SQLAlchemy Engine, Session setup, and Base)
└── frontend/ (React App)
├── src/
│ ├── context/ThemeContext.jsx
│ ├── components/
│ └── App.jsx

## 2. Backend (FastAPI + SQLAlchemy) Requirements

### 2.1. Database Configuration

- **Engine & Base:** Use SQLAlchemy to connect to the SQLite file `sqlite:///./backend/app.db`.
- **Dependency:** Implement a `get_db()` dependency to manage database sessions for API endpoints.
- **Initialization:** The application must ensure the `app.db` file and the necessary tables are created on startup if they don't already exist.
- **Initial Data:** Include a function to populate the `campaigns` table with at least one sample entry upon first table creation.

### 2.2. SQLAlchemy ORM Models (`models/orm.py`)

- **`Campaign` Table:**
  - `id`: Primary Key (UUID String).
  - `campaign_message`: Text.
  - `target_region`: Text.
  - `target_audience`: Text.
  - `brand_images`: Text (to store a JSON string of relative image paths).
- **`Product` Table:**
  - `id`: Primary Key (UUID String).
  - `campaign_id`: Foreign Key linking to `Campaign.id`.
  - `name`, `description`: Text.
  - `image_path`: Text (Relative path to file in `/files/media/`).
- **`Post` Table:**
  - `id`: Primary Key (UUID String).
  - `campaign_id`: Foreign Key linking to `Campaign.id`.
  - `product_id`: Foreign Key linking to `Product.id`.
  - `headline`: Text (Short, punchy headline for image overlay).
  - `body_text`: Text (Main post content, 2-3 sentences).
  - `caption`: Text (Social media caption).
  - `text_color`: Text (Hex color code for headline background, e.g., "#FF4081").
  - `image_1_1`: Text (Relative path to 1:1 aspect ratio image).
  - `image_16_9`: Text (Relative path to 16:9 aspect ratio image).
  - `image_9_16`: Text (Relative path to 9:16 aspect ratio image).
  - `generation_prompt`: Text (User's prompt used for generation).
  - `created_at`: DateTime.

### 2.3. Pydantic Schemas (`models/pydantic.py`)

- Define a schema (`CampaignRead`) for the output of the `/api/campaigns` endpoint, ensuring all required fields are present and using Python types.

### 2.4. Static Files

- The **FastAPI app must mount** the local `/files` directory to the public URL prefix **`/static`** (e.g., `app.mount("/static", StaticFiles(directory="files"), name="static")`).

## 3. Frontend (React/Tailwind) Requirements

- **Aesthetic:** Neo-Brutalist/Minimalist with dark/light theme support.
- **Theme:** Implement a `ThemeContext` to manage theme state and apply the `dark` class to the `<html>` element.
- **Initial View:** Fetch and display the list of campaigns in a top-level dropdown upon loading the app.

## 4. Initial Deliverable Focus (Phase 1)

Focus on the structure, database models, database creation, the static file serving, and the single API endpoint: `GET /api/campaigns`.

5. Data Ingestion Flow (Batch & Manual)

The UI uses a two-tabbed modal for creation: Batch Load (JSON/YAML upload) and Manual Form. The backend's validation dictates the transition between these two modes.

5.1. Campaign Creation Flow

FE Action (Batch): The user selects the New Campaign button and uploads a JSON or YAML file via the Batch Load tab drop area.

BE Endpoint: The file content is sent to a dedicated FastAPI endpoint (e.g., POST /api/campaigns/validate).

BE Validation & Conversion:

If YAML, the content is parsed and converted to a Python dictionary.

The dictionary is validated against the Pydantic CampaignCreate schema.

If non-optional, required fields (e.g., campaign_message, target_region) are missing, the endpoint returns a partial 200 OK response containing the data that was present and a list of missing fields.

FE Response Handling:

Success: If the BE returns a complete data object (no missing fields), the FE proceeds to the final database write step.

Partial Data: If the BE returns missing fields, the FE automatically switches the modal to the Manual Form tab, pre-populating all available data fields from the response object, allowing the user to complete the missing non-optional inputs.

FE Action (Final Submit): The user submits the final, complete form data (now including uploaded brand images, which are handled by a separate multi-part form submission).

BE Database Action: A unique campaignId (UUID) is generated, and the new record is committed to the SQLite campaigns table.

5.2. Product Creation Flow

FE Action (Batch): The user clicks Add Product (within an active campaign) and uploads a JSON file containing product metadata via the Batch Load tab.

BE Endpoint: The file content is sent to a dedicated FastAPI endpoint (e.g., POST /api/products/validate). The campaignId of the current campaign is included in the request URL.

BE Validation:

The data is validated against the Pydantic ProductCreate schema.

Validation checks if the required metadata (name, description) is present.

Image upload is decoupled here: The batch JSON is for metadata only; image upload occurs during the manual form completion.

FE Response Handling: Similar to campaigns, if required fields are missing, the FE switches to the Manual Form tab, pre-filling data.

FE Action (Final Submit) & Image Upload: The user completes the manual form and uploads the necessary product image via a file input. The image is sent to a separate endpoint (POST /api/media/upload).

BE File/Database Action:

The image is saved to /files/media/.

The relative path (media/image\_<UUID>.png) is retrieved.

A unique productId is generated, and the new record (including the campaign_id FK and the image_path) is committed to the SQLite products table.

## 6. AI-Powered Post Generation (Phase 3) ✅ COMPLETED

### 6.1. Overview

The Posts feature generates professional social media content using Google's Gemini 2.5 AI models and PIL image compositing. The system creates both text content (headline, body text, caption) and stylized product images with text overlays for multiple aspect ratios.

### 6.2. Two-Step AI Generation Process

**Step 1: Text Generation (Gemini 2.5 Flash)**
- Generates headline, body_text, caption based on campaign and product context
- Suggests vibrant hex color for headline background (#FF4081, #00BCD4, etc.)
- Returns structured JSON output

**Step 2: Image Generation & Compositing**
- **2a. Stylized Image Generation (Gemini 2.5 Flash Image)**
  - Takes product image as input (img2img)
  - Applies campaign-appropriate styling, lighting, atmosphere
  - Keeps product recognizable while enhancing visual appeal
  - Returns transformed PIL Image

- **2b. Headline Overlay (PIL/Pillow)**
  - Uses Gemini-generated image as canvas
  - Adds HUGE stylized headline with vibrant colored background
  - Neo-brutalist style: thick black borders (8px), white text with stroke
  - Adds brand logo watermark in corner
  - Saves to structured path: `posts/{CampaignName}_{Headline}/image_1-1.png`

### 6.3. Gemini Service (`services/gemini_service.py`)

**Models Used:**
- `gemini-2.5-flash` - Text generation (headline, body, caption, color)
- `gemini-2.5-flash-image` - Image generation and editing (img2img)

**Methods:**
- `generate_post_copy()` - Generates text content with structured JSON output
- `build_system_prompt()` - Crafts professional copywriter prompt with campaign context
- `parse_gemini_response()` - Extracts JSON from Gemini response
- `generate_product_image()` - Generates stylized product image using img2img
- `_build_image_prompt()` - Creates detailed image transformation prompt

**Text Generation Prompt Strategy:**
- Professional social media copywriter persona
- Includes campaign message, CTA, target audience, product details
- User's custom prompt for creative direction
- Requests structured JSON: `{headline, body_text, caption, text_color}`
- Enforces character limits (headline: 60 chars, body: 280 chars, caption: 150 chars)

**Image Generation Prompt Strategy:**
- Transform product image while maintaining recognizability
- Add campaign-appropriate atmosphere and styling
- Enhance visual appeal for social media
- Keep product as main focus

### 6.4. Image Compositor (`services/image_compositor.py`)

**Canvas Sizes:**
- 1:1 → 1080x1080 (Instagram square)
- 16:9 → 1920x1080 (Landscape/YouTube)
- 9:16 → 1080x1920 (Story/Vertical)

**Font Sizes (HUGE for Impact):**
- 1:1 → 120px
- 16:9 → 100px
- 9:16 → 140px

**Compositing Process:**
1. Use Gemini-generated image as base canvas
2. Resize to target aspect ratio dimensions
3. Add brand logo overlay (small, bottom-right corner)
4. Add HUGE stylized headline with:
   - Vibrant colored background (from Gemini suggestion)
   - Thick black border (8px) for neo-brutalist aesthetic
   - White text with black stroke for maximum contrast
   - Smart text wrapping to fit canvas width
5. Add final border to entire image
6. Save to structured path

**Font Loading:**
- Tries multiple system font paths with fallbacks
- Logs which font loaded successfully
- Uses DejaVuSans-Bold, LiberationSans-Bold, or NotoSans-Bold

### 6.5. Posts API Endpoints (`api/posts.py`)

**Endpoints:**
- `GET /api/posts?campaign_id={id}` - List posts for campaign
- `GET /api/posts/{id}` - Get single post
- `POST /api/posts` - Create post manually
- `POST /api/posts/generate` - **AI generate post (Main endpoint)**
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post

**Generate Endpoint Flow:**
```python
POST /api/posts/generate
Body: {
  campaign_id: "uuid",
  product_id: "uuid",
  prompt: "User's creative direction",
  aspect_ratios: ["1:1", "16:9", "9:16"]
}

Process:
1. Fetch campaign data (message, audience, brand images)
2. Fetch product data (name, description, image)
3. Generate text with Gemini 2.5 Flash
4. For each aspect ratio:
   a. Generate stylized image with Gemini 2.5 Flash Image (img2img)
   b. Composite headline overlay with PIL
   c. Save to /files/posts/{CampaignName}_{Headline}/
5. Create Post record in database
6. Return PostRead with all image paths
```

**Comprehensive Logging:**
- Step-by-step progress tracking with emoji indicators
- Detailed error messages for troubleshooting
- Font loading success/failure logs
- Image generation confirmations

### 6.6. Frontend - Posts Page

**Components:**
- `PostsPage.jsx` - Main posts page with grid layout
- `PostCard.jsx` - Instagram-style compact card with aspect ratio selector
- `PostGenerateForm.jsx` - AI generation form with product selector

**PostCard Features:**
- Aspect ratio selector buttons (Square, Landscape, Story)
- Displays headline, body_text, caption
- Three action buttons: Edit, Download, Delete
- Compact design similar to ProductCard
- Grid layout: 3 columns on desktop, 1-2 on mobile

**PostGenerateForm Features:**
- Product dropdown (filtered by selected campaign)
- Prompt textarea with placeholder examples
- Aspect ratio checkboxes (1:1, 16:9, 9:16)
- Generate button with loading spinner
- Progress messages during generation

### 6.7. File Storage Structure

```
/files/posts/
  ├── {CampaignName}_{PostHeadline}/
  │   ├── image_1-1.png
  │   ├── image_16-9.png
  │   └── image_9-16.png
```

**Filename Sanitization:**
- Remove special characters
- Replace spaces with underscores
- Remove consecutive underscores
- Truncate headline to 50 characters

### 6.8. Environment Configuration

**Required Environment Variables (.env):**
```
GEMINI_API_KEY=your_api_key_here
```

**Dependencies (requirements.txt):**
```
google-generativeai>=0.8.0
Pillow>=10.0.0
httpx>=0.25.0
python-dotenv>=1.0.0
```
