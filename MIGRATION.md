# Database Migration - Campaign Name Field Added

## Changes Made

### Schema Updates:
1. **Added `name` field** to Campaign model (required field)
2. Updated Campaign dropdown to show **name** instead of message
3. Added **tabbed modals** for JSON upload + Manual form
4. Updated all example JSON files with campaign names

---

## 🔧 Migration Steps

### Step 1: Delete Old Database
The schema has changed, so you need to delete the old database file:

**On Windows:**
```bash
cd backend
del app.db
```

**On Mac/Linux:**
```bash
cd backend
rm app.db
```

### Step 2: Restart Backend
The database will automatically recreate with the new schema:

```bash
uvicorn main:app --reload
```

You should see:
```
✅ Database tables created/verified
✅ Seeded initial campaign data
```

### Step 3: Frontend is Ready
No changes needed - just refresh your browser at http://localhost:5173

---

## ✨ New Features

### 1. Campaign Name Field
- Campaigns now have a **name** field (required)
- Dropdown shows campaign **name** instead of truncated message
- Example: "Summer 2025 Water Bottle Launch"

### 2. Tabbed Modals
When clicking "+ New Campaign" or "+ Add Product", you now see tabs:
- **Manual Tab**: Fill out the form manually
- **JSON Tab**: Upload a JSON file

### 3. JSON Upload Flow
1. Click "+ New Campaign"
2. Switch to "JSON" tab
3. Click "Choose JSON File"
4. Select `examples/campaign-complete.json` or `campaign-incomplete.json`
5. If **complete**: Form fills and you can submit
6. If **incomplete**: Switch to "Manual" tab and fill remaining fields

### 4. Brand Images Display
Campaign details now show actual brand images in a grid (not just paths)

---

## 📋 Updated JSON Format

### Campaign JSON (Complete):
```json
{
  "name": "Summer 2025 Water Bottle Launch",
  "campaign_message": "Summer 2025 Product Launch - Eco-Friendly Water Bottles",
  "target_region": "North America",
  "target_audience": "Health-conscious millennials and Gen-Z aged 18-35",
  "brand_images": "[\"https://picsum.photos/400/300?random=1\"]"
}
```

### Campaign JSON (Incomplete):
```json
{
  "name": "Winter Holiday 2025",
  "campaign_message": "Winter Holiday Collection 2025",
  "brand_images": "[\"https://picsum.photos/400/300?random=3\"]"
}
```
*Missing: target_region, target_audience*

---

## 🧪 Testing the New Features

### Test Campaign Creation:
1. Click "+ New Campaign"
2. Go to "JSON" tab
3. Upload `examples/campaign-complete.json`
4. Form should auto-fill
5. Click "Create Campaign"
6. New campaign appears in dropdown showing **name**

### Test Incomplete JSON:
1. Click "+ New Campaign"
2. Go to "JSON" tab
3. Upload `examples/campaign-incomplete.json`
4. See message: "Incomplete data. Please fill: target_region, target_audience"
5. Switch to "Manual" tab
6. Form is partially filled (name & message present)
7. Complete the missing fields
8. Submit successfully

### Test Product JSON:
1. Select a campaign
2. Click "+ Add Product"
3. Go to "JSON" tab
4. Upload `examples/product-single.json`
5. Form fills with product data
6. Submit to create product with image

---

## 🚨 Troubleshooting

### Error: "Campaign name is required"
- The `name` field is now mandatory
- Update any custom JSON files to include `"name": "Your Campaign Name"`

### Error: "no such column: campaigns.name"
- You forgot to delete the old `app.db` file
- Delete it and restart the backend

### Dropdown shows old truncated messages
- Clear browser cache or hard refresh (Ctrl+Shift+R)
- Make sure backend restarted after deleting database

---

## 📦 What's Next

All set for continued development! The app now has:
- ✅ Campaign name field in schema
- ✅ Tabbed modals (JSON + Manual)
- ✅ Improved dropdown UX
- ✅ JSON validation with incomplete data handling
- ✅ Image display for products and campaigns
- ✅ URL download for images

Ready for Phase 4: AI Creative Generation! 🤖🎨
