# NIST 800-61 Ticketing System Setup

## Prerequisites
- Python 3.8+
- Node.js (optional, only if you want to extend frontend with a framework later)
- Modern Web Browser

## Installation

1.  **Backend Setup**
    Navigate to the project root and install dependencies:
    ```powershell
    pip install -r requirements.txt
    ```

2.  **Run the Backend**
    Start the FastAPI server:
    ```powershell
    uvicorn backend.main:app --reload
    ```
    The API will be available at `http://127.0.0.1:8000`.

3.  **Run the Frontend**
    - **Local Choice**: Open `docs/index.html` in your browser.
    - **GitHub Pages**: Push this repository to GitHub and configure Pages to serve from the `/docs` folder. The site will be available at `https://<user>.github.io/ISC2_Support/`.

    *Note: The frontend is configured to talk to `http://localhost:8000`. You must have the backend running locally for the GitHub Pages site to work on your machine.*

## Features Implemented
- **Ticket Submission**: NIST-aligned form (Identification & Reporting).
- **Admin Dashboard**: View and filter tickets (Analysis & Tracking).
- **Auto-Triage**: AI rule-based classification.
- **Metrics**: MTTR tracking with `Resolved At` timestamps.
- **Export**: CSV export for compliance reporting.

## Project Structure
- `backend/`: FastAPI application (API, Database, Models).
- `docs/`: Frontend code (ready for GitHub Pages).
