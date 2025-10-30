"""
Media API router for file uploads.
"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from services.file_manager import save_uploaded_file


router = APIRouter()


@router.post("/media/upload", response_model=dict)
async def upload_media(file: UploadFile = File(...)):
    """
    Upload an image file to the media directory.

    Args:
        file: The uploaded image file

    Returns:
        Dictionary with the file path

    Raises:
        400: If file type not allowed or upload failed
    """
    file_path = await save_uploaded_file(file)

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload file. Ensure it's a valid image."
        )

    return {
        "file_path": file_path,
        "message": "File uploaded successfully"
    }


@router.post("/media/upload/multiple", response_model=dict)
async def upload_multiple_media(files: List[UploadFile] = File(...)):
    """
    Upload multiple image files.

    Args:
        files: List of uploaded files

    Returns:
        Dictionary with file paths and any errors
    """
    uploaded_paths = []
    errors = []

    for file in files:
        file_path = await save_uploaded_file(file)
        if file_path:
            uploaded_paths.append(file_path)
        else:
            errors.append(f"Failed to upload {file.filename}")

    return {
        "file_paths": uploaded_paths,
        "errors": errors,
        "total_uploaded": len(uploaded_paths),
        "total_failed": len(errors)
    }
