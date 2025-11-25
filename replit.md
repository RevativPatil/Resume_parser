# AI Resume Screening System

## Overview
An intelligent resume parsing and screening system built with FastAPI and Groq's ultra-fast LLM API. This application automatically extracts structured information from resumes in multiple formats and provides AI-powered skill-based candidate search.

**Current Status**: ✅ Fully configured and running on Replit

**Last Updated**: November 25, 2024

## Features
- **Multi-format Support**: Upload resumes in PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
- **AI-Powered Parsing**: Uses Groq's Llama 3.3 70B model for intelligent entity extraction
- **Smart Search**: Skill-based candidate matching with experience and education filters
- **SQLite Database**: Lightweight database for storing parsed candidate data
- **Modern Web UI**: Clean, responsive interface for HR teams
- **High Performance**: Groq API provides 200-300 tokens/second

## Project Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11)
- **LLM Provider**: Groq API (llama-3.3-70b-versatile)
- **Database**: SQLite (for development)
- **OCR**: Tesseract (for image-based resumes)
- **Frontend**: Vanilla JavaScript with modern CSS

### Directory Structure
```
├── app.py                 # Main FastAPI application
├── config.py              # Configuration and environment settings
├── database/
│   ├── models.py         # SQLAlchemy database models
├── services/
│   ├── file_processor.py # File parsing (PDF, DOCX, images)
│   ├── groq_parser.py    # Groq API integration
│   ├── llm_parser.py     # LLM parsing wrapper
│   └── search_engine.py  # Candidate search logic
├── static/
│   ├── script.js         # Frontend JavaScript
│   └── style.css         # Frontend styling
├── templates/
│   └── index.html        # Main web interface
├── utils/
│   ├── helpers.py        # Utility functions
│   └── validation.py     # Input validation
└── uploads/              # Resume file storage
```

## Configuration

### Environment Variables
The following environment variables are configured in Replit:

- `GROQ_API_KEY` (Secret): Your Groq API key from https://console.groq.com/
- `DATABASE_URL`: SQLite database path (sqlite:///./resume_parser.db)
- `GROQ_MODEL`: LLM model to use (llama-3.3-70b-versatile)
- `DEBUG`: Enable debug mode (True)

### Groq API
- Free tier: 5,000 requests/day
- Available models in config:
  - `llama-3.3-70b-versatile` (current, recommended)
  - `mixtral-8x7b-32768` (fastest, 32K context)
  - `llama2-70b-4096` (very capable)

## How It Works

### Resume Upload Flow
1. User uploads resume file via web interface
2. Backend extracts text using appropriate parser (PDF/DOCX/OCR)
3. Text is sent to Groq API for entity extraction
4. Structured data is saved to SQLite database
5. File is stored in `uploads/` directory

### Entities Extracted
- Personal Info: Name, email, phone, location
- Skills: All technical skills, tools, frameworks
- Education: Degrees, institutions, years, fields of study
- Experience: Job titles, companies, durations, descriptions

### Search Functionality
- Searches candidates by skills (fuzzy matching)
- Filters by minimum years of experience
- Filters by education level
- Returns ranked results with match scores

## Development Notes

### Running Locally
The application is configured to run automatically via Replit workflow:
```bash
python app.py
```
Server runs on: http://0.0.0.0:5000

### Database Management
Database is automatically created on first run. Use these utilities:
- `setup_database.py` - Initialize database tables
- `view_database.py` - View database contents
- `test_database.py` - Test database connection

### Testing
Test files included:
- `test_groq.py` - Test Groq API connection
- `check_groq_models.py` - Check available models
- `test_resume.txt` - Sample resume for testing

## User Preferences
None specified yet.

## Recent Changes
- **Nov 25, 2024**: Initial Replit setup
  - Configured Python 3.11 environment
  - Installed all dependencies (FastAPI, Groq, SQLAlchemy, etc.)
  - Set up SQLite database for development
  - Configured Groq API integration
  - Created workflow for FastAPI server on port 5000
  - Server successfully running and accessible

## Known Issues
- Using SQLite instead of PostgreSQL (user didn't have database provisioning permissions)
- LSP diagnostics showing some import warnings (non-critical)

## Future Enhancements
- PostgreSQL integration for production
- Advanced search filters (location, salary expectations)
- Resume comparison features
- Email notifications for new candidates
- Batch upload support
- Export to CSV/Excel
