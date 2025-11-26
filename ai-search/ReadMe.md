# Google AI Site Search (FastAPI + Gemini AI)

A FastAPI backend service that integrates with **Google Gemini AI** to provide PDF-based document search and question answering. This service is designed to work with Google Sites and handles automatic file upload, caching, and secure CORS restrictions.

## Features

- **FastAPI Backend:** Lightweight, fast, and production-ready API server.
- **Google Gemini AI Integration:** Uses Gemini’s `generate_content` API to answer questions based on uploaded PDFs.
- **Self-Healing File Uploads:** Automatically uploads and caches PDF files, ensuring availability.
- **CORS Security:** Restricts access to specific environments.
- **Logging & Error Handling:** Detailed logging for debugging and safe error messages for clients.

## Repo Structure

```text
├── index.html          # Frontend page for Google Site or testing
├── main.py             # FastAPI backend application
├── requirements.txt    # Python dependencies
├── research_paper.pdf  # PDF file used for document search
└── README.md           # Project documentation
```

---

## Requirements

- Python 3.10+  
- [FastAPI](https://fastapi.tiangolo.com/)  
- [Google GenAI SDK](https://pypi.org/project/google-genai/)  
- [python-dotenv](https://pypi.org/project/python-dotenv/)  
- Optional: Uvicorn for running the server  

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configure Environment Variables

Create a file named `.env` in the root directory and add your Google API key:

```ini
GOOGLE_API_KEY=your_actual_api_key_here
```

## Add Your Document

Ensure a file named `research_paper.pdf` (or the filename specified in main.py) exists in the root directory.

## How It Works

1. On startup, the server attempts to **upload and cache the PDF** to Google Gemini.
2. When a `/search` request is made, it ensures the file is **active and ready**.
3. Sends the PDF and user question to **Gemini AI** with strict research assistant instructions.
4. Returns the generated answer or an appropriate error.

## Notes

- Make sure `research_paper.pdf` exists in the project root.  
- The file caching system prevents unnecessary re-uploads and automatically handles expired files.  

## Logging

- Logs are written to the console.  
- Includes warnings for expired files, errors during upload, and generation issues.