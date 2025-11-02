"""
Google Cloud Storage Service for managing mood media files.

Handles uploading and deleting mood media to/from GCS bucket.
Provides fallback to local-only storage if GCS credentials not configured.
"""
import os
import json
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()

# GCS configuration from environment
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "").strip()
GCS_PROJECT_ID = os.getenv("GCS_PROJECT_ID", "").strip()
GCS_CREDENTIALS_JSON = os.getenv("GCS_CREDENTIALS_JSON", "").strip()
GCS_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()

# Check if GCS is enabled (need bucket + project + credentials)
GCS_ENABLED = bool(GCS_BUCKET_NAME and GCS_PROJECT_ID and (GCS_CREDENTIALS_JSON or GCS_CREDENTIALS_PATH))

logger.info(f"🔍 GCS Configuration Check:")
logger.info(f"    GCS_BUCKET_NAME: {GCS_BUCKET_NAME if GCS_BUCKET_NAME else 'NOT SET'}")
logger.info(f"    GCS_PROJECT_ID: {GCS_PROJECT_ID if GCS_PROJECT_ID else 'NOT SET'}")
logger.info(f"    GCS_CREDENTIALS_JSON: {'SET (%d chars)' % len(GCS_CREDENTIALS_JSON) if GCS_CREDENTIALS_JSON else 'NOT SET'}")
logger.info(f"    GCS_CREDENTIALS_PATH: {GCS_CREDENTIALS_PATH if GCS_CREDENTIALS_PATH else 'NOT SET'}")
logger.info(f"    GCS_ENABLED: {GCS_ENABLED}")

if GCS_ENABLED:
    try:
        from google.cloud import storage
        logger.info(f"✅ GCS enabled: bucket={GCS_BUCKET_NAME}, project={GCS_PROJECT_ID}")
    except ImportError:
        logger.error("❌ google-cloud-storage package not installed. Run: pip install google-cloud-storage")
        GCS_ENABLED = False
else:
    logger.warning("⚠️ GCS not configured in .env - mood media will only be stored locally")
    logger.warning("⚠️ Veo video generation with reference images will not work")


class GCSService:
    """
    Service for uploading/deleting mood media to/from Google Cloud Storage.
    """

    def __init__(self):
        """Initialize GCS client if enabled."""
        self.enabled = GCS_ENABLED
        self.bucket_name = GCS_BUCKET_NAME
        self.client = None
        self.bucket = None

        if self.enabled:
            try:
                # Initialize GCS client
                if GCS_CREDENTIALS_JSON:
                    # Parse embedded JSON credentials
                    try:
                        credentials_dict = json.loads(GCS_CREDENTIALS_JSON)
                        self.client = storage.Client.from_service_account_info(
                            credentials_dict,
                            project=GCS_PROJECT_ID
                        )
                        logger.info(f"✅ GCS client initialized from embedded JSON credentials")
                    except json.JSONDecodeError as e:
                        logger.error(f"❌ Invalid GCS_CREDENTIALS_JSON format: {str(e)}")
                        self.enabled = False
                        return
                elif GCS_CREDENTIALS_PATH and os.path.exists(GCS_CREDENTIALS_PATH):
                    # Use file path
                    self.client = storage.Client.from_service_account_json(
                        GCS_CREDENTIALS_PATH,
                        project=GCS_PROJECT_ID
                    )
                    logger.info(f"✅ GCS client initialized from credentials file")
                else:
                    # Use application default credentials
                    self.client = storage.Client(project=GCS_PROJECT_ID)
                    logger.info(f"✅ GCS client initialized from default credentials")

                self.bucket = self.client.bucket(GCS_BUCKET_NAME)
                logger.info(f"✅ GCS bucket connected: {GCS_BUCKET_NAME}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize GCS client: {str(e)}")
                self.enabled = False

    def upload_mood_file(self, file_data: bytes, filename: str, content_type: str) -> Optional[str]:
        """
        Upload mood media file to GCS bucket in /moods/ folder.

        Args:
            file_data: Binary file data
            filename: Filename (e.g., "campaign_img_20250111_143022_1-1.png")
            content_type: MIME type (e.g., "image/png", "video/mp4")

        Returns:
            GCS URI (gs://bucket/moods/filename) or None if GCS disabled/failed
        """
        if not self.enabled:
            logger.error(f"  ❌ GCS not enabled - cannot upload {filename}")
            logger.error(f"  ❌ Check .env configuration:")
            logger.error(f"      GCS_BUCKET_NAME: {'SET' if GCS_BUCKET_NAME else 'MISSING'}")
            logger.error(f"      GCS_PROJECT_ID: {'SET' if GCS_PROJECT_ID else 'MISSING'}")
            logger.error(f"      GCS_CREDENTIALS_JSON: {'SET' if GCS_CREDENTIALS_JSON else 'MISSING'}")
            logger.error(f"      GCS_CREDENTIALS_PATH: {'SET' if GCS_CREDENTIALS_PATH else 'MISSING'}")
            return None

        try:
            # Upload to /moods/ folder
            blob_path = f"moods/{filename}"
            logger.info(f"  🔄 Uploading to bucket: {self.bucket_name}, path: {blob_path}")
            blob = self.bucket.blob(blob_path)

            # Upload with content type
            blob.upload_from_string(file_data, content_type=content_type)

            # Make publicly readable (optional - remove if you want private files)
            # blob.make_public()

            gcs_uri = f"gs://{self.bucket_name}/{blob_path}"
            logger.info(f"  ✅ Uploaded to GCS: {gcs_uri}")
            return gcs_uri

        except Exception as e:
            logger.error(f"  ❌ GCS upload failed for {filename}")
            logger.error(f"  ❌ Error type: {type(e).__name__}")
            logger.error(f"  ❌ Error message: {str(e)}")
            import traceback
            logger.error(f"  ❌ Traceback: {traceback.format_exc()}")
            return None

    def delete_mood_file(self, gcs_uri: str) -> bool:
        """
        Delete mood media file from GCS bucket.

        Args:
            gcs_uri: Full GCS URI (e.g., "gs://bucket/moods/file.png")

        Returns:
            True if deleted successfully, False otherwise
        """
        if not self.enabled or not gcs_uri:
            return False

        try:
            # Extract blob path from URI
            # gs://bucket/moods/file.png -> moods/file.png
            if not gcs_uri.startswith(f"gs://{self.bucket_name}/"):
                logger.warning(f"  ⚠️ Invalid GCS URI format: {gcs_uri}")
                return False

            blob_path = gcs_uri.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_path)

            # Delete blob
            blob.delete()
            logger.info(f"  ✅ Deleted from GCS: {gcs_uri}")
            return True

        except Exception as e:
            logger.error(f"  ❌ GCS delete failed: {str(e)}")
            return False

    def download_mood_file(self, gcs_uri: str) -> Optional[bytes]:
        """
        Download mood media file from GCS bucket.

        Args:
            gcs_uri: Full GCS URI (e.g., "gs://bucket/moods/file.png")

        Returns:
            File bytes or None if download failed
        """
        if not self.enabled or not gcs_uri:
            return None

        try:
            # Extract blob path from URI
            # gs://bucket/moods/file.png -> moods/file.png
            if not gcs_uri.startswith(f"gs://{self.bucket_name}/"):
                logger.warning(f"  ⚠️ Invalid GCS URI format: {gcs_uri}")
                return None

            blob_path = gcs_uri.replace(f"gs://{self.bucket_name}/", "")
            blob = self.bucket.blob(blob_path)

            # Download blob
            file_data = blob.download_as_bytes()
            logger.info(f"  ✅ Downloaded from GCS: {gcs_uri} ({len(file_data)} bytes)")
            return file_data

        except Exception as e:
            logger.error(f"  ❌ GCS download failed: {str(e)}")
            return None

    def is_enabled(self) -> bool:
        """Check if GCS is enabled and configured."""
        return self.enabled


# Create singleton instance
gcs_service = GCSService()
