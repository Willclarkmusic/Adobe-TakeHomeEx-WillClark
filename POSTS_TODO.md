# 🎨 Posts Feature - Implementation TODO

## Overview
AI-powered post generation using Gemini for copywriting and PIL for image compositing.

---

## Phase 1: Backend Setup ✅ IN PROGRESS

### Database & Models
- [ ] Install google-generativeai package (`pip install google-generativeai`)
- [ ] Install Pillow for image compositing (`pip install Pillow`)
- [ ] Add `GEMINI_API_KEY` to backend/.env
- [ ] Create Post ORM model in `models/orm.py`
  - Fields: id, campaign_id, product_id, headline, body_text, caption
  - Fields: image_1_1, image_16_9, image_9_16, generation_prompt, created_at
- [ ] Create Post Pydantic schemas in `models/pydantic.py`
  - PostCreate, PostUpdate, PostRead, PostGenerateRequest
- [ ] Update database.py to create posts table

### File Storage Structure
```
/files/posts/
  ├── {CampaignName}_{PostHeadline}/
  │   ├── image_1-1.png
  │   ├── image_16-9.png
  │   └── image_9-16.png
```

---

## Phase 2: Gemini Integration

### Service Creation
- [ ] Create `services/gemini_service.py`
- [ ] Implement `GeminiService` class with:
  - [ ] `__init__()` - Configure API with key
  - [ ] `generate_post_copy()` - Main generation method
  - [ ] `build_system_prompt()` - Craft professional copywriter prompt
  - [ ] `parse_gemini_response()` - Extract JSON from response

### System Prompt Design
The prompt should include:
- Campaign message and CTA
- Target audience and region
- Product name and description
- User's custom prompt
- Request structured JSON output: {headline, body_text, caption}

### Testing
- [ ] Test text generation with sample data
- [ ] Verify JSON parsing
- [ ] Handle API errors gracefully

---

## Phase 3: Image Compositing

### Service Creation
- [ ] Create `services/image_compositor.py`
- [ ] Implement `ImageCompositor` class with:
  - [ ] `create_post_image()` - Main compositing method
  - [ ] `get_canvas_size()` - Calculate dimensions for aspect ratio
  - [ ] `composite_product_image()` - Add product image
  - [ ] `add_brand_elements()` - Add brand images as watermark/overlay
  - [ ] `add_text_overlay()` - Add headline/caption with proper typography
  - [ ] `save_image()` - Save to structured path

### Template Design (Per Aspect Ratio)
- [ ] **1:1 (1080x1080)** - Instagram square
  - Product image centered/hero
  - Brand logo in corner
  - Text overlay at bottom
- [ ] **16:9 (1920x1080)** - Landscape/YouTube
  - Product image left, text right
  - Brand elements subtle
- [ ] **9:16 (1080x1920)** - Story/Vertical
  - Product image top 2/3
  - Text overlay bottom 1/3

### Testing
- [ ] Test each aspect ratio
- [ ] Verify file naming convention
- [ ] Check image quality

---

## Phase 4: API Endpoints

### Posts Router (`api/posts.py`)
- [ ] Create posts router file
- [ ] Implement endpoints:
  - [ ] `GET /api/posts?campaign_id={id}` - List posts for campaign
  - [ ] `GET /api/posts/{id}` - Get single post
  - [ ] `POST /api/posts` - Create post manually
  - [ ] `POST /api/posts/generate` - AI generate post (THE BIG ONE)
  - [ ] `PUT /api/posts/{id}` - Update post
  - [ ] `DELETE /api/posts/{id}` - Delete post + images
- [ ] Register router in main.py

### Generate Endpoint Logic
```python
@router.post("/posts/generate")
async def generate_post(request: PostGenerateRequest):
    1. Fetch campaign data
    2. Fetch product data
    3. Call GeminiService.generate_post_copy()
    4. For each selected aspect ratio:
       - Call ImageCompositor.create_post_image()
    5. Create Post record in DB
    6. Return PostRead with all image paths
```

---

## Phase 5: Frontend - PostsPage Rebuild

### Component Structure
- [ ] Create `components/PostCard.jsx` - Display post with images
- [ ] Create `components/PostForm.jsx` - Manual/JSON/Generate tabs
- [ ] Create `components/PostGenerateTab.jsx` - AI generation UI
- [ ] Update `pages/PostsPage.jsx` - Main posts page

### PostsPage Features
- [ ] Post grid/list display
- [ ] "+ Create Post" button
- [ ] Loading states
- [ ] Empty state (no posts yet)
- [ ] Delete confirmation

### PostCard Features
- [ ] Display all generated aspect ratios
- [ ] Show headline, body_text, caption
- [ ] Edit button
- [ ] Delete button
- [ ] Download buttons (per aspect ratio)
- [ ] Regenerate button (future enhancement)

### PostForm - Generate Tab
- [ ] Product selector dropdown (fetch products for campaign)
- [ ] Prompt textarea with placeholder
- [ ] Aspect ratio checkboxes:
  - [x] 1:1 (default)
  - [ ] 16:9
  - [ ] 9:16
- [ ] Generate button (with loading spinner)
- [ ] Preview section (shows generated content before saving)
- [ ] Save button (after generation preview)

### State Management
- [ ] `posts` state array
- [ ] `loadingPosts` state
- [ ] `showPostModal` state
- [ ] `editingPost` state
- [ ] `generatingPost` state (for AI generation loading)

---

## Phase 6: Integration & Polish

### API Integration
- [ ] Create post fetching method
- [ ] Create post saving method
- [ ] Create post generation method
- [ ] Create post deletion method

### Error Handling
- [ ] Handle Gemini API errors
- [ ] Handle image generation errors
- [ ] Handle file system errors
- [ ] Display user-friendly error messages

### Loading States
- [ ] Show spinner during text generation
- [ ] Show progress for image generation ("Generating 1:1...", "Generating 16:9...")
- [ ] Disable form during generation

### UX Polish
- [ ] Success message after generation
- [ ] Confirmation before delete
- [ ] Image zoom/preview modal
- [ ] Copy to clipboard buttons (for caption text)

---

## Phase 7: Testing & Validation

### Backend Testing
- [ ] Test Gemini API integration
- [ ] Test image generation for all aspect ratios
- [ ] Test file naming convention
- [ ] Test CRUD operations

### Frontend Testing
- [ ] Test post creation flow
- [ ] Test post generation flow
- [ ] Test aspect ratio selection
- [ ] Test edit/delete functionality

### End-to-End Testing
- [ ] Generate post with all 3 aspect ratios
- [ ] Verify images saved correctly
- [ ] Verify posts display correctly
- [ ] Test across different campaigns/products

---

## Future Enhancements (Not in scope for now)

- [ ] Regenerate individual aspect ratios
- [ ] Edit post text and regenerate images
- [ ] Batch generate multiple posts
- [ ] Schedule posts
- [ ] Export posts as ZIP
- [ ] A/B test different prompts
- [ ] Post performance tracking

---

## Notes

### File Naming Convention
```
/files/posts/Summer_2025_Launch_Hydrate_in_Style/
  ├── image_1-1.png
  ├── image_16-9.png
  └── image_9-16.png
```

### Sanitization Rules
- Campaign name: Remove special chars, replace spaces with underscores
- Post headline: Same rules, truncate to 50 chars
- Aspect ratios: Use hyphens (1-1, 16-9, 9-16) for valid filenames

### Gemini Prompt Strategy
- Use Gemini Pro (text only) for copywriting
- Structured output: Request JSON format explicitly
- Include examples in system prompt for consistency
- Professional copywriter persona

### Image Compositing Strategy
- Use PIL/Pillow (no external API needed)
- Pre-designed templates per aspect ratio
- Dynamic text sizing based on content length
- Brand-consistent color scheme from campaign

---

## Progress Tracking

**Phase 1:** ⬜ Not Started
**Phase 2:** ⬜ Not Started
**Phase 3:** ⬜ Not Started
**Phase 4:** ⬜ Not Started
**Phase 5:** ⬜ Not Started
**Phase 6:** ⬜ Not Started
**Phase 7:** ⬜ Not Started

**Total Progress:** 0% (0/70 tasks completed)
