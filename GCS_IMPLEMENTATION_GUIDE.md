# Google Cloud Storage Integration Guide

## Overview

This guide explains how to integrate your existing Google Cloud Storage bucket with the Mood Board feature for Veo video generation with reference images.

## ✅ What's Been Implemented

### 1. **Database Schema Updates**
- Added `gcs_uri` field to `MoodMedia` table to store GCS URIs alongside local paths
- Updated Pydantic schemas to include `gcs_uri` in API responses

### 2. **GCS Service** (`backend/services/gcs_service.py`)
- Handles uploading mood media (images/videos) to GCS bucket
- Handles deleting mood media from GCS bucket
- All files uploaded to `/moods/` folder in your bucket
- Graceful fallback if GCS not configured

### 3. **Automatic Upload/Delete**
- All generated mood images → uploaded to GCS
- All generated mood videos → uploaded to GCS
- All manually uploaded files → uploaded to GCS
- When deleting mood media → deleted from both local filesystem AND GCS

### 4. **Veo Reference Images**
- Video generation now uses GCS URIs for reference images
- Falls back to prompt-only if GCS not configured
- Supports up to 3 reference images (Veo limit)

---

## 📋 Setup Instructions

### Step 1: Configure Environment Variables

Edit `backend/.env` and add your GCS configuration:

```bash
# Google Cloud Storage Configuration (for Veo reference images)
GCS_BUCKET_NAME=your-actual-bucket-name
GCS_PROJECT_ID=your-gcp-project-id
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account-key.json
```

**Example:**
```bash
GCS_BUCKET_NAME=creative-automation-bucket
GCS_PROJECT_ID=my-project-123456
GOOGLE_APPLICATION_CREDENTIALS=/mnt/h/React_Dev/Adobe-Take-Home/backend/gcs-key.json
```

### Step 2: Get Service Account Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **IAM & Admin** → **Service Accounts**
3. Create a new service account (or use existing)
4. Grant permissions: **Storage Object Admin** (for read/write/delete)
5. Create a JSON key for this service account
6. Download the JSON file
7. Place it in your backend directory (e.g., `backend/gcs-key.json`)
8. Update `GOOGLE_APPLICATION_CREDENTIALS` path in `.env`

### Step 3: Verify Bucket Configuration

Make sure your GCS bucket:
- Exists in your GCP project
- Has the service account with proper permissions
- Is in the same region as your Gemini/Veo API usage (recommended for performance)

### Step 4: Install Required Package

```bash
cd backend
pip install google-cloud-storage
```

### Step 5: Database Migration

Since we added a new field, you need to update your database:

**Option A: Drop and recreate (development only - loses all data):**
```bash
cd backend
rm app.db
# Restart backend - it will recreate tables
```

**Option B: Add column manually (preserves data):**
```bash
cd backend
sqlite3 app.db
```

Then run:
```sql
ALTER TABLE moods_media ADD COLUMN gcs_uri TEXT;
.quit
```

### Step 6: Restart Backend

```bash
cd backend
python main.py
```

You should see logs like:
```
✅ GCS enabled: bucket=your-bucket, project=your-project
✅ GCS client initialized successfully
```

---

## 🧪 Testing

### Test 1: Generate Mood Image

1. Go to Mood Board page
2. Click "Image Controls"
3. Generate an image
4. Check logs for:
   ```
   ✅ Saved locally: moods/Campaign_img_20250111_143022_1-1.png
   ✅ Uploaded to GCS: gs://your-bucket/moods/Campaign_img_20250111_143022_1-1.png
   ```

### Test 2: Generate Video with Reference Images

1. Generate at least one mood image first (so it has a GCS URI)
2. Click "Video Controls"
3. Select the generated image as reference
4. Generate video
5. Check logs for:
   ```
   ✓ Found GCS URI for moods/Campaign_img_20250111_143022_1-1.png
   📸 Using 1 GCS reference images
   ✓ Added GCS reference image 1: gs://your-bucket/moods/...
   🎬 Calling Veo API with 1 reference images...
   ```

### Test 3: Delete Mood Media

1. Delete a mood image/video
2. Check logs for:
   ```
   ✅ Deleted from GCS: gs://your-bucket/moods/file.png
   ✅ Successfully deleted mood media
   ```
3. Verify file is gone from GCS bucket

---

## ⚠️ Fallback Behavior (No GCS Configured)

If you don't configure GCS (leave .env empty):

- ✅ Mood images/videos still work (saved locally only)
- ✅ Manual uploads still work (saved locally only)
- ⚠️ Video generation with reference images will show warnings:
  ```
  ⚠️ Reference images provided but no GCS URIs available
  ⚠️ This happens if GCS is not configured in .env
  ⚠️ Generating video from prompt only (reference images ignored)
  ```
- ✅ Video generation still works (just without reference images)

---

## 📁 File Structure in GCS

All mood media uploaded to `/moods/` folder:

```
gs://your-bucket/
  └── moods/
      ├── Campaign_img_20250111_143022_1-1.png
      ├── Campaign_img_20250111_143022_16-9.png
      ├── Campaign_vid_20250111_150500_16-9.mp4
      └── Campaign_upload_20250111_160000.png
```

---

## 🔍 Database Schema

The `moods_media` table now includes:

| Column | Type | Description |
|--------|------|-------------|
| `file_path` | TEXT | Local relative path (e.g., `moods/file.png`) |
| `gcs_uri` | TEXT | GCS URI (e.g., `gs://bucket/moods/file.png`) |

- `file_path` → Used for serving via `/static/` endpoint
- `gcs_uri` → Used for Veo reference images

---

## 🐛 Troubleshooting

### Issue: "GCS client initialization failed"

**Solution:** Check service account credentials:
```bash
# Verify JSON key file exists
ls -la backend/gcs-key.json

# Check file has valid JSON
cat backend/gcs-key.json | python -m json.tool

# Verify service account has Storage Object Admin role
```

### Issue: "Permission denied" when uploading to GCS

**Solution:** Grant Storage Object Admin role to service account:
1. Go to GCS bucket → Permissions
2. Add service account email
3. Grant role: **Storage Object Admin**

### Issue: Reference images not working for videos

**Checklist:**
- ✅ GCS is configured in `.env`
- ✅ Mood images have `gcs_uri` in database (generate new images after GCS setup)
- ✅ Selected reference images are mood images (not products)
- ✅ Check logs for "Found GCS URI" messages

---

## 💡 Best Practices

1. **Region Consistency:** Use same region for GCS bucket and Gemini API calls
2. **Cost Management:** GCS storage costs ~$0.02/GB/month
3. **Backup:** Keep local files as backup (`files/moods/`)
4. **Security:** Don't commit service account JSON to git (add to `.gitignore`)
5. **Monitoring:** Watch GCS logs for upload/download activity

---

## 📊 Cost Estimation

| Item | Cost |
|------|------|
| GCS Storage | ~$0.02/GB/month |
| GCS Operations | $0.004 per 1000 writes |
| Veo Video Gen | Varies by model |

**Example:** 1000 mood images (~2MB each) = ~2GB = **$0.04/month**

---

## 🚀 Next Steps

1. ✅ Configure `.env` with your GCS credentials
2. ✅ Install `google-cloud-storage` package
3. ✅ Update database schema (add `gcs_uri` column)
4. ✅ Restart backend
5. ✅ Test image generation → verify GCS upload
6. ✅ Test video generation with reference images
7. ✅ Monitor logs for any errors

---

## 📝 Summary

With GCS integration:
- **All mood media** automatically backed up to cloud storage
- **Veo video generation** can use reference images from GCS
- **Graceful fallback** if GCS not configured
- **Automatic cleanup** when deleting media

This enables the full power of Veo 3.1's reference image capabilities! 🎉
