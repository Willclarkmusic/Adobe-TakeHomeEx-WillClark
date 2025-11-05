# 📡 API Documentation

Complete API reference for the Creative Automation Hub backend.

## Base Configuration

- **Base URL**: `http://localhost:8000`
- **API Prefix**: `/api` (most endpoints)
- **Authentication**: None (open API)
- **CORS**: Enabled for all origins
- **Content Type**: `application/json` (unless specified otherwise)

## Static Endpoints

- **Static Files**: `http://localhost:8000/static/*` - Serves from `/files/` directory
- **Examples**: `http://localhost:8000/examples/*` - Serves sample JSON files
- **API Docs**: `http://localhost:8000/docs` - Interactive Swagger UI documentation

---

## 🏢 Campaigns API

Manage marketing campaigns with brand information and targeting.

### List All Campaigns
```http
GET /api/campaigns
```

**Response**: `200 OK`
```json
[
  {
    "id": "uuid-string",
    "name": "Summer 2025 Launch",
    "campaign_message": "Introducing our eco-friendly collection",
    "call_to_action": "Shop Now!",
    "target_region": "North America",
    "target_audience": "Millennials 25-35",
    "brand_images": "[\"path1.jpg\", \"path2.jpg\"]",
    "start_date": "2025-06-01",
    "duration": 30
  }
]
```

---

### Get Single Campaign
```http
GET /api/campaigns/{campaign_id}
```

**Path Parameters**:
- `campaign_id` (string, required) - Campaign UUID

**Response**: `200 OK` - Campaign object
**Errors**: `404 Not Found` - Campaign not found

---

### Validate Campaign Data
```http
POST /api/campaigns/validate
```

**Purpose**: Validate campaign data from JSON upload. Used in batch load flow to check for missing required fields before switching to manual entry.

**Request Body**:
```json
{
  "name": "Campaign Name",
  "campaign_message": "Message text",
  "call_to_action": "Click here",
  "brand_images": "[\"image1.jpg\"]",
  "products": []
}
```

**Response**: `200 OK`
```json
{
  "data": { /* submitted data */ },
  "missing_fields": ["target_region", "target_audience"],
  "is_complete": false
}
```

**Required Fields**: `name`, `campaign_message`, `target_region`, `target_audience`

**Special Features**:
- Preserves optional `products` array for nested creation
- Returns partial data for form pre-filling

---

### Create Campaign
```http
POST /api/campaigns
```

**Purpose**: Create a new campaign with auto-generated UUID. Processes brand images (downloads URLs or copies local files).

**Request Body**:
```json
{
  "name": "Summer 2025 Launch",
  "campaign_message": "Eco-friendly collection for conscious consumers",
  "call_to_action": "Shop Now!",
  "target_region": "North America",
  "target_audience": "Eco-conscious millennials aged 25-35",
  "brand_images": "[\"https://example.com/logo.png\"]",
  "start_date": "2025-06-01",
  "duration": 30
}
```

**Response**: `201 Created` - Campaign object

**Special Features**:
- Downloads remote URLs to local storage
- Copies local file paths to `/files/media/`
- Generates unique filenames with UUIDs

---

### Create Campaign with Products
```http
POST /api/campaigns/with-products
```

**Purpose**: Create campaign and all products in a single atomic transaction. Perfect for batch JSON uploads.

**Request Body**:
```json
{
  "name": "Summer 2025 Launch",
  "campaign_message": "Eco-friendly collection",
  "target_region": "North America",
  "target_audience": "Millennials 25-35",
  "brand_images": "[\"logo1.png\", \"logo2.png\"]",
  "products": [
    {
      "name": "Eco Water Bottle",
      "description": "Sustainable stainless steel bottle",
      "image_path": "https://example.com/bottle.jpg"
    },
    {
      "name": "Bamboo Utensils",
      "description": "Reusable cutlery set",
      "image_path": "examples/Campora_assets/product_utensils.jpg"
    }
  ]
}
```

**Response**: `201 Created`
```json
{
  "campaign": { /* campaign object */ },
  "products": [ /* array of created products */ ]
}
```

**Special Features**:
- Atomic transaction - all succeed or all fail
- Processes all brand images and product images
- Uses flush() to get campaign ID before creating products

---

### Update Campaign
```http
PUT /api/campaigns/{campaign_id}
```

**Purpose**: Partially update campaign fields. Only updates provided fields.

**Path Parameters**:
- `campaign_id` (string, required)

**Request Body** (all fields optional):
```json
{
  "name": "Updated Campaign Name",
  "brand_images": "[\"new-logo.png\"]"
}
```

**Response**: `200 OK` - Updated campaign
**Errors**: `404 Not Found` - Campaign not found

**Special Features**: Processes brand images if updated

---

### Delete Campaign
```http
DELETE /api/campaigns/{campaign_id}
```

**Purpose**: Delete campaign and all associated products (cascade delete).

**Path Parameters**:
- `campaign_id` (string, required)

**Response**: `204 No Content`
**Errors**: `404 Not Found` - Campaign not found

---

## 📦 Products API

Manage campaign products with images and descriptions.

### List All Products
```http
GET /api/products?campaign_id={campaign_id}
```

**Query Parameters**:
- `campaign_id` (string, optional) - Filter by campaign

**Response**: `200 OK` - Array of products

---

### Get Single Product
```http
GET /api/products/{product_id}
```

**Path Parameters**:
- `product_id` (string, required)

**Response**: `200 OK` - Product object
**Errors**: `404 Not Found` - Product not found

---

### Get Products by Campaign
```http
GET /api/campaigns/{campaign_id}/products
```

**Path Parameters**:
- `campaign_id` (string, required)

**Response**: `200 OK` - Array of products
**Errors**: `404 Not Found` - Campaign not found

---

### Validate Single Product
```http
POST /api/products/validate
```

**Purpose**: Validate product data from JSON upload. Checks for required fields.

**Request Body**:
```json
{
  "name": "Product Name",
  "description": "Product description",
  "image_path": "product.jpg",
  "campaign_id": "uuid-string"
}
```

**Response**: `200 OK`
```json
{
  "data": { /* submitted data */ },
  "missing_fields": [],
  "is_complete": true
}
```

**Required Fields**: `name`, `campaign_id`

---

### Validate Batch Products
```http
POST /api/products/batch/validate
```

**Purpose**: Validate multiple products from batch JSON upload.

**Request Body**:
```json
[
  {
    "name": "Product 1",
    "description": "Description 1",
    "image_path": "product1.jpg"
  },
  {
    "name": "Product 2",
    "description": "Description 2"
  }
]
```

**Response**: `200 OK`
```json
{
  "valid_products": [ /* products that passed validation */ ],
  "invalid_products": [
    {
      "index": 0,
      "data": { /* product data */ },
      "errors": "Missing required field: campaign_id"
    }
  ],
  "is_complete": false
}
```

---

### Create Batch Products
```http
POST /api/products/batch
```

**Purpose**: Create multiple products in a single atomic transaction. All-or-nothing operation.

**Request Body**:
```json
{
  "products": [
    {
      "campaign_id": "uuid-string",
      "name": "Product 1",
      "description": "Description 1",
      "image_path": "https://example.com/product1.jpg"
    },
    {
      "campaign_id": "uuid-string",
      "name": "Product 2",
      "description": "Description 2",
      "image_path": "examples/Campora_assets/product2.jpg"
    }
  ]
}
```

**Response**: `201 Created` - Array of created products
**Errors**:
- `404 Not Found` - Campaign not found
- `500 Internal Server Error` - Any product creation failed (transaction rolled back)

**Special Features**:
- Atomic transaction
- Processes all image paths (URLs and local files)
- Verifies all campaigns exist before processing

---

### Create Single Product
```http
POST /api/products
```

**Request Body**:
```json
{
  "campaign_id": "uuid-string",
  "name": "Eco Water Bottle",
  "description": "Sustainable stainless steel bottle",
  "image_path": "https://example.com/bottle.jpg"
}
```

**Response**: `201 Created` - Product object
**Errors**: `404 Not Found` - Campaign not found

---

### Update Product
```http
PUT /api/products/{product_id}
```

**Path Parameters**:
- `product_id` (string, required)

**Request Body** (all fields optional):
```json
{
  "name": "Updated Product Name",
  "description": "New description"
}
```

**Response**: `200 OK` - Updated product
**Errors**: `404 Not Found` - Product not found

---

### Delete Product
```http
DELETE /api/products/{product_id}
```

**Path Parameters**:
- `product_id` (string, required)

**Response**: `204 No Content`
**Errors**: `404 Not Found` - Product not found

---

### Regenerate Product Image (AI)
```http
POST /api/products/{product_id}/regenerate-image
```

**Purpose**: Generate a new product image using AI when the current image is missing or unreadable. Uses Google Gemini to create a professional product photo from the product's name and description.

**Path Parameters**:
- `product_id` (string, required) - Product UUID

**Request Body** (optional):
```json
{
  "user_prompt": "modern minimalist style"
}
```

**Request Fields**:
- `user_prompt` (string, optional) - Style or mood guidance for image generation

**Response**: `200 OK` - Updated product with new image_path
```json
{
  "id": "uuid-string",
  "campaign_id": "uuid-string",
  "name": "Camping Tent",
  "description": "4-person weatherproof tent",
  "image_path": "/static/media/product_Camping_Tent_abc12345.png"
}
```

**Errors**:
- `404 Not Found` - Product not found
- `500 Internal Server Error` - Image generation or save failed

**How It Works**:
1. Creates a neutral 1080x1080 gray base template
2. Uses Gemini img2img to transform template into professional product photo
3. Generates from: product name + description + optional style prompt
4. Saves to `/files/media/product_{name}_{uuid}.png`
5. Updates product.image_path in database

**Use Cases**:
- Product has missing image file
- Product has unreadable/corrupted image (AVIF, HEIC, etc.)
- Temporary placeholder needed during data import
- Quick asset generation for prototyping

**Generation Time**: ~10-20 seconds per image

---

## 🎨 Posts API (AI-Generated Content)

Create and manage social media posts with AI-generated text and images.

### List All Posts
```http
GET /api/posts?campaign_id={campaign_id}
```

**Query Parameters**:
- `campaign_id` (string, optional) - Filter by campaign

**Response**: `200 OK` - Array of posts (ordered by created_at descending)

```json
[
  {
    "id": "uuid-string",
    "campaign_id": "uuid-string",
    "product_id": "uuid-string",
    "mood_id": null,
    "source_images": "[\"media/product.jpg\"]",
    "headline": "Summer Vibes Are Here",
    "body_text": "Get ready for the hottest season...",
    "caption": "Tag a friend! #SummerVibes",
    "text_color": "#FF4081",
    "image_1_1": "posts/Campaign_Headline/image_1-1.png",
    "image_16_9": "posts/Campaign_Headline/image_16-9.png",
    "image_9_16": "posts/Campaign_Headline/image_9-16.png",
    "generation_prompt": "Create vibrant summer vibe",
    "created_at": "2025-01-30T12:00:00"
  }
]
```

---

### Get Single Post
```http
GET /api/posts/{post_id}
```

**Path Parameters**:
- `post_id` (string, required)

**Response**: `200 OK` - Post object
**Errors**: `404 Not Found` - Post not found

---

### Get Available Images for Post Generation
```http
GET /api/posts/available-images?campaign_id={campaign_id}
```

**Purpose**: Get all available source images for post generation (products + mood board images). Used by PostGenerateForm selector.

**Query Parameters**:
- `campaign_id` (string, required)

**Response**: `200 OK`
```json
{
  "products": [
    {
      "id": "uuid",
      "campaign_id": "uuid",
      "name": "Product Name",
      "description": "Description",
      "image_path": "/static/media/product.jpg"
    }
  ],
  "mood_images": [
    {
      "id": "uuid",
      "campaign_id": "uuid",
      "file_path": "moods/image.png",
      "media_type": "image",
      "aspect_ratio": "1:1"
    }
  ]
}
```

---

### Generate Post with AI ⭐
```http
POST /api/posts/generate
```

**Purpose**: Main AI generation endpoint. Creates social media post with Gemini-generated text and images.

**Request Body**:
```json
{
  "campaign_id": "uuid-string",
  "source_images": [
    "/static/media/product.jpg",
    "moods/mood-image.png"
  ],
  "prompt": "Create a vibrant summer vibe post highlighting eco-friendly features",
  "aspect_ratios": ["1:1", "16:9", "9:16"]
}
```

**Response**: `201 Created` - Post object with all generated content

**Process Flow**:
1. **Load Sources**: Fetch campaign data and load source images
2. **Determine Origin**: Track if source is product or mood board
3. **Generate Text**: Use Gemini 2.5 Flash to create headline, body_text, caption, text_color
4. **Generate Images**: For each aspect ratio:
   - Single source: img2img transformation with Gemini 2.5 Flash Image
   - Multiple sources: Composition/blend with Gemini 2.5 Flash Image
   - Add logo overlay and neo-brutalist border with PIL
   - Save to `/files/posts/{CampaignName}_{Headline}/image_{ratio}.png`
5. **Create Record**: Store post in database with source tracking

**Special Features**:
- **Random Logo Selection**: Picks one brand logo randomly, uses for all aspect ratios
- **Smart Generation Strategy**:
  - 1 source image → img2img transformation
  - 2+ source images → Composition/blend
- **Consistent Base Image**: First ratio generates base, others adapt it
- **Source Tracking**: Records product_id or mood_id based on source
- **Comprehensive Logging**: Emoji indicators for each step

**Aspect Ratios**:
- `1:1` → 1080x1080 (Instagram square)
- `16:9` → 1920x1080 (Landscape/YouTube)
- `9:16` → 1080x1920 (Story/Vertical)

**Errors**:
- `400 Bad Request` - Invalid aspect ratio or generation failed
- `404 Not Found` - Campaign or source images not found
- `500 Internal Server Error` - Post generation failed

---

### Create Post Manually
```http
POST /api/posts
```

**Purpose**: Create post without AI generation (manual entry).

**Request Body**:
```json
{
  "campaign_id": "uuid-string",
  "product_id": "uuid-string",
  "headline": "Manual Post Headline",
  "body_text": "Manual post content",
  "caption": "Manual caption",
  "text_color": "#FF4081",
  "image_1_1": "path/to/image.png"
}
```

**Response**: `201 Created` - Post object
**Errors**: `404 Not Found` - Campaign or product not found

---

### Update Post
```http
PUT /api/posts/{post_id}
```

**Purpose**: Update post fields (partial update).

**Path Parameters**:
- `post_id` (string, required)

**Request Body** (all fields optional):
```json
{
  "headline": "Updated Headline",
  "caption": "Updated caption"
}
```

**Response**: `200 OK` - Updated post
**Errors**: `404 Not Found` - Post not found

---

### Regenerate Post Images
```http
PUT /api/posts/{post_id}/regenerate
```

**Purpose**: Regenerate images for existing post with new settings. Keeps existing text content (headline, body, caption, color).

**Path Parameters**:
- `post_id` (string, required)

**Request Body**:
```json
{
  "product_id": "uuid-string",
  "prompt": "New creative direction",
  "aspect_ratios": ["1:1", "9:16"]
}
```

**Response**: `200 OK` - Updated post with new images

**Process**:
1. Get existing post, campaign, product
2. Delete old image folder
3. Generate new images using **existing** headline, body, caption, color
4. Update post with new image paths and prompt

**Errors**:
- `400 Bad Request` - Invalid aspect ratio
- `404 Not Found` - Post, campaign, or product not found
- `500 Internal Server Error` - Regeneration failed

---

### Delete Post
```http
DELETE /api/posts/{post_id}
```

**Purpose**: Delete post and all associated image files.

**Path Parameters**:
- `post_id` (string, required)

**Response**: `204 No Content`
**Errors**: `404 Not Found` - Post not found

**Special Features**: Deletes entire post folder from filesystem

---

## 📤 Media API

Upload and manage media files.

### Upload Single Image
```http
POST /api/media/upload
```

**Content-Type**: `multipart/form-data`

**Form Data**:
- `file` (file, required) - Image file to upload

**Response**: `200 OK`
```json
{
  "file_path": "/static/media/upload_uuid.jpg",
  "message": "File uploaded successfully"
}
```

**Allowed Extensions**: `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.svg`

**Errors**: `400 Bad Request` - Invalid file type or upload failed

**Special Features**:
- Generates unique filename with UUID
- Validates file extension
- Saves to `/files/media/`

---

### Upload Multiple Images
```http
POST /api/media/upload/multiple
```

**Content-Type**: `multipart/form-data`

**Form Data**:
- `files` (file[], required) - Array of image files

**Response**: `200 OK`
```json
{
  "file_paths": ["/static/media/upload_uuid1.jpg", "/static/media/upload_uuid2.png"],
  "errors": ["file3.txt: Invalid file type"],
  "total_uploaded": 2,
  "total_failed": 1
}
```

**Special Features**: Partial success allowed (some files may fail)

---

## 🎭 Moods API (Mood Board)

Generate and manage mood board images and videos.

### List Mood Media
```http
GET /api/moods?campaign_id={campaign_id}
```

**Query Parameters**:
- `campaign_id` (string, required)

**Response**: `200 OK` - Array of mood media (ordered by created_at descending)

```json
[
  {
    "id": "uuid-string",
    "campaign_id": "uuid-string",
    "file_path": "moods/Campaign_img_20250130_120000_1-1.png",
    "gcs_uri": null,
    "media_type": "image",
    "is_generated": true,
    "prompt": "Vibrant summer aesthetic",
    "source_images": "[\"media/product.jpg\"]",
    "aspect_ratio": "1:1",
    "generation_metadata": "{\"model\": \"gemini-2.5-flash-image\"}",
    "created_at": "2025-01-30T12:00:00"
  }
]
```

---

### Get Available Images for Mood Generation
```http
GET /api/moods/available-images?campaign_id={campaign_id}
```

**Purpose**: Get available source images for mood generation (products + existing mood images). Used by MoodPopup selector.

**Query Parameters**:
- `campaign_id` (string, required)

**Response**: `200 OK`
```json
{
  "products": [ /* array of products */ ],
  "mood_images": [ /* array of existing mood images */ ]
}
```

---

### Generate Mood Images ⭐
```http
POST /api/moods/images/generate
```

**Purpose**: Generate 1-3 mood board images using Gemini. Each ratio generates a completely separate, distinct image.

**Request Body**:
```json
{
  "campaign_id": "uuid-string",
  "prompt": "Vibrant summer beach aesthetic with warm tones",
  "source_images": [
    "/static/media/product.jpg",
    "moods/existing-mood.png"
  ],
  "ratios": ["1:1", "9:16"]
}
```

**Valid Ratios**: `1:1`, `3:4`, `4:3`, `9:16`, `16:9`

**Response**: `200 OK` - Array of generated mood media objects

**Validation**:
- Maximum 3 aspect ratios
- Total source images size must be under 17MB

**Special Features**:
- Each ratio generates independent image with distinct styling
- Date-stamped filenames: `CampaignName_img_YYYYMMDDHHmmss_ratio.png`
- Saves to `/files/moods/`
- Creates DB record with `is_generated=True`

**Errors**:
- `400 Bad Request` - Invalid ratios, too many ratios, or images exceed 17MB
- `500 Internal Server Error` - Generation failed
- `504 Gateway Timeout` - Generation timeout

---

### Generate Mood Video ⭐
```http
POST /api/moods/videos/generate
```

**Purpose**: Generate mood board video using Veo. Async operation taking 30-60 seconds.

**Request Body**:
```json
{
  "campaign_id": "uuid-string",
  "prompt": "Dynamic summer beach scene with ocean waves",
  "source_images": [
    "/static/media/product1.jpg",
    "/static/media/product2.jpg"
  ],
  "ratio": "16:9",
  "duration": 6
}
```

**Parameters**:
- `ratio` (string) - `16:9` or `9:16`
- `duration` (int) - `4`, `6`, or `8` seconds

**Response**: `200 OK` - Mood media object with video

**Validation**:
- Maximum 3 source images
- Ratio must be `16:9` or `9:16`
- Duration must be 4, 6, or 8 seconds
- Total source images size under 17MB

**Special Features**:
- Polls until video complete (30-60 seconds)
- Date-stamped filename: `CampaignName_vid_YYYYMMDDHHmmss_ratio.mp4`
- Saves to `/files/moods/`
- Creates DB record with `is_generated=True`

**Errors**:
- `400 Bad Request` - Invalid parameters or images exceed 17MB
- `500 Internal Server Error` - Generation failed
- `504 Gateway Timeout` - Video generation timeout

---

### Upload Mood Media
```http
POST /api/moods/upload?campaign_id={campaign_id}
```

**Purpose**: Manually upload mood media file (image or video).

**Content-Type**: `multipart/form-data`

**Query Parameters**:
- `campaign_id` (string, required)

**Form Data**:
- `file` (file, required) - Image or video file

**Response**: `200 OK` - Mood media object

**Special Features**:
- Accepts both images and videos
- Date-stamped filenames
- Sets `is_generated=False`
- Stores original filename in metadata

**Errors**:
- `400 Bad Request` - Invalid file type
- `404 Not Found` - Campaign not found
- `500 Internal Server Error` - Upload failed

---

### Delete Mood Media
```http
DELETE /api/moods/{mood_id}
```

**Path Parameters**:
- `mood_id` (string, required)

**Response**: `204 No Content`
**Errors**:
- `404 Not Found` - Mood media not found
- `500 Internal Server Error` - Delete failed

**Special Features**: Deletes both file and database record

---

## 📮 Deploy API (Social Media Posting)

Schedule and post content to social media via Ayrshare.

### Get Connected Profiles
```http
GET /api/deploy/profiles
```

**Purpose**: Get all connected social media profiles from Ayrshare account.

**Response**: `200 OK`
```json
{
  "profiles": [
    {
      "profile_key": "ayrshare-profile-id",
      "platform": "instagram",
      "username": "@myaccount",
      "display_name": "My Account",
      "is_active": true
    },
    {
      "profile_key": "ayrshare-profile-id-2",
      "platform": "twitter",
      "username": "@mytwitter",
      "display_name": "My Twitter",
      "is_active": true
    }
  ]
}
```

**Supported Platforms**: Instagram, Facebook, Twitter, LinkedIn, Pinterest, TikTok, YouTube

**Errors**: `500 Internal Server Error` - Ayrshare API call failed

**Requirements**: `AYRSHARE_API_KEY` must be set in `.env`

---

### Schedule Social Media Post ⭐
```http
POST /api/deploy/schedule-post
```

**Purpose**: Schedule a social media post via Ayrshare. Supports immediate, scheduled, and recurring posts.

**Request Body**:
```json
{
  "post_id": "uuid-string",
  "campaign_id": "uuid-string",
  "schedule_type": "scheduled",
  "platforms": ["instagram", "facebook"],
  "schedule_time": "2025-06-01T10:00:00",
  "recurring_config": null
}
```

**Schedule Types**:

**1. Immediate Posting**
```json
{
  "schedule_type": "immediate",
  "platforms": ["instagram"],
  ...
}
```
Posts approximately 10 seconds from now.

**2. Scheduled Posting**
```json
{
  "schedule_type": "scheduled",
  "schedule_time": "2025-06-01T10:00:00",
  "platforms": ["instagram", "facebook"],
  ...
}
```
Posts at specific future time.

**3. Recurring Posting**
```json
{
  "schedule_type": "recurring",
  "platforms": ["instagram"],
  "recurring_config": {
    "repeat": 5,
    "days": 3,
    "order": "sequential",
    "post_ids": ["post1-uuid", "post2-uuid"]
  },
  ...
}
```
Automatically reposts multiple times with interval.

**Recurring Config**:
- `repeat` (int): Number of times to repeat (1-10)
- `days` (int): Interval between posts in days (2+)
- `order` (string): `"sequential"` or `"random"`
- `post_ids` (List[string]): Post IDs for rotation

**Response**: `200 OK` - Scheduled post object with nested post data

**Special Features**:
- Builds post text from caption + body_text
- Automatically selects first available aspect ratio for media
- Tracks status: `"pending"` or `"posted"`
- Stores Ayrshare post ID for future reference

**Errors**:
- `400 Bad Request` - Invalid schedule_type or missing required fields
- `404 Not Found` - Post or campaign not found
- `500 Internal Server Error` - Scheduling failed

---

### Get Scheduled Posts
```http
GET /api/deploy/scheduled-posts?campaign_id={campaign_id}
```

**Query Parameters**:
- `campaign_id` (string, required)

**Response**: `200 OK` - Array of scheduled posts (ordered by created_at descending)

```json
[
  {
    "id": "uuid-string",
    "post_id": "uuid-string",
    "campaign_id": "uuid-string",
    "schedule_type": "scheduled",
    "platforms": "[\"instagram\", \"facebook\"]",
    "schedule_time": "2025-06-01T10:00:00",
    "recurring_config": null,
    "ayrshare_post_id": "ayrshare-id",
    "status": "pending",
    "error_message": null,
    "created_at": "2025-01-30T12:00:00",
    "post": {
      "id": "uuid",
      "headline": "Post Headline",
      "caption": "Post caption",
      "image_1_1": "posts/path/image.png"
    }
  }
]
```

**Errors**: `404 Not Found` - Campaign not found

---

### Cancel Scheduled Post
```http
DELETE /api/deploy/scheduled-posts/{scheduled_post_id}
```

**Purpose**: Cancel/delete scheduled post from both Ayrshare and local database.

**Path Parameters**:
- `scheduled_post_id` (string, required)

**Response**: `204 No Content`
**Errors**:
- `404 Not Found` - Scheduled post not found
- `500 Internal Server Error` - Failed to cancel

**Special Features**:
- Deletes from Ayrshare API if `ayrshare_post_id` exists
- Deletes from local database

---

## 🏥 Health Check

### Root Endpoint
```http
GET /
```

**Response**: `200 OK`
```json
{
  "message": "Creative Automation Hub API is running",
  "status": "healthy",
  "docs": "/docs"
}
```

---

## 🔧 Common Patterns

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Image Path Processing
All image path fields support three formats:
1. **Remote URLs**: `https://example.com/image.jpg` - Downloaded automatically
2. **Local Paths**: `examples/Campora_assets/logo.png` - Copied to media directory
3. **Processed Paths**: `/static/media/image_uuid.jpg` - Already stored, used as-is

### File Storage Structure
```
/files/
├── media/              # Uploaded images and brand logos
│   ├── upload_uuid1.jpg
│   └── image_uuid2.png
├── posts/              # AI-generated post images
│   └── CampaignName_Headline/
│       ├── image_1-1.png
│       ├── image_16-9.png
│       └── image_9-16.png
└── moods/              # Mood board media
    ├── Campaign_img_20250130_120000_1-1.png
    └── Campaign_vid_20250130_120000_16-9.mp4
```

### Filename Sanitization
- Special characters removed
- Spaces replaced with underscores
- Consecutive underscores removed
- Campaign names truncated to 50 characters

---

## 🚀 AI Features

### Models Used
- **Gemini 2.5 Flash**: Text generation (headlines, body text, captions, colors)
- **Gemini 2.5 Flash Image**: Image generation and transformation (img2img)
- **Veo 3.1**: Video generation for mood boards

### AI Capabilities
1. **Post Generation** (`POST /api/posts/generate`)
   - Text: Headlines, body copy, captions, color suggestions
   - Images: img2img transformation or multi-image composition
   - Output: 1-3 aspect ratios per post

2. **Product Image Regeneration** (`POST /api/products/{id}/regenerate-image`)
   - Generates professional product photos from text descriptions
   - Uses: Missing/corrupted images, quick prototyping
   - Output: 1080x1080 square product photo

3. **Mood Board Images** (`POST /api/moods/generate-image`)
   - Creates inspirational visual content
   - Can blend multiple source images
   - Output: 1-5 separate images at different ratios

4. **Mood Board Videos** (`POST /api/moods/generate-video`)
   - Cinematic video generation with Veo
   - 4-8 second duration
   - Supports 1 reference image

### Important Limitations
- **Gemini Flash Image**: Only supports img2img (image-to-image transformation), NOT pure text-to-image
- **Product Regeneration**: Requires base template for img2img transformation
- **Veo Reference Images**: Maximum 1 reference image per video (Veo limitation)

### Size Limits
- **Mood Generation**: 17MB total for source images
- **File Uploads**: No explicit limit (configured in server)

### Aspect Ratios
**Posts**:
- `1:1` - 1080x1080 (Instagram square)
- `16:9` - 1920x1080 (Landscape/YouTube)
- `9:16` - 1080x1920 (Story/Vertical)

**Mood Images**:
- `1:1` - Square
- `3:4` - Portrait
- `4:3` - Landscape
- `9:16` - Vertical story
- `16:9` - Horizontal video

**Mood Videos**:
- `16:9` - Horizontal (4, 6, or 8 seconds)
- `9:16` - Vertical (4, 6, or 8 seconds)

### Image Composition Features
- Random logo selection from brand images
- Neo-brutalist styling with thick borders (8px)
- HUGE stylized headlines (120px-140px fonts)
- Smart text wrapping and positioning
- Vibrant colored backgrounds
- Consistent base image adapted across ratios

---

## 📚 Additional Resources

- **Interactive API Docs**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc format)
- **Repository**: See README.md for setup instructions
- **Quick Start**: See QUICK_START.md for getting started

---

## 🔐 Authentication

Currently, the API does not implement authentication. All endpoints are publicly accessible. In a production environment, you should implement:
- API key authentication
- OAuth2/JWT tokens
- Rate limiting
- CORS restrictions to specific origins

---

## ⚙️ Configuration

### Required Environment Variables
```bash
# Required
GEMINI_API_KEY=your_gemini_api_key_here

# Optional (for Deploy features)
AYRSHARE_API_KEY=your_ayrshare_api_key_here
```

### Database
- **Type**: SQLite
- **Location**: `backend/app.db`
- **Auto-Initialize**: Tables created on first run
- **Seed Data**: Sample campaign inserted on first run

---

*Last Updated: January 2025*
