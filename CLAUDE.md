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
│ ├── api/
│ │ ├── campaigns.py (Router)
│ │ └── products.py
│ ├── services/
│ │ └── file_manager.py
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
