# Local Setup Guide - AI Resume Screening System

This guide will help you run the AI Resume Screening application on your local machine.

## Prerequisites

Before starting, ensure you have:
- **Python 3.11+** installed ([Download here](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **Git** (optional, to clone the repository)
- **Tesseract OCR** (required for image-based resumes)

## Step 1: Get Your Groq API Key

1. Visit [https://console.groq.com/](https://console.groq.com/)
2. Sign up for a free account (if you don't have one)
3. Create a new API key
4. Copy the key (you'll need it later)
5. Free tier includes 5,000 requests/day

## Step 2: Install Tesseract OCR

### Windows
1. Download the installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (default installation path is fine)
3. The installer will add Tesseract to your PATH automatically

### macOS
```bash
brew install tesseract
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get install tesseract-ocr
```

## Step 3: Clone or Download the Project

```bash
# Option 1: Clone from Replit (if available)
git clone <your-replit-url>
cd resume-parser

# Option 2: Download as ZIP and extract
# Then navigate to the project folder
cd path/to/resume-parser
```

## Step 4: Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

## Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages:
- FastAPI (web framework)
- Groq (LLM API client)
- SQLAlchemy (database ORM)
- pdfplumber (PDF parsing)
- python-docx (Word document parsing)
- pytesseract (OCR)
- And more...

## Step 6: Configure Environment Variables

Create a `.env` file in the project root directory with:

```env
GROQ_API_KEY=your-groq-api-key-here
DATABASE_URL=sqlite:///./resume_parser.db
GROQ_MODEL=llama-3.3-70b-versatile
DEBUG=True
```

**Important:** Replace `your-groq-api-key-here` with your actual Groq API key from Step 1.

## Step 7: Run the Application

```bash
python app.py
```

You should see output like:
```
Starting Resume Parser Server...
Database URL: sqlite:///./resume_parser.db
Groq Model: llama-3.3-70b-versatile
Server will be available at: http://0.0.0.0:5000
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:5000
```

## Step 8: Access the Application

Open your browser and go to:
```
http://localhost:5000
```

You should see the AI Resume Screening interface!

---

## Troubleshooting

### Issue: "No module named 'fastapi'"
**Solution:** Make sure your virtual environment is activated and you ran `pip install -r requirements.txt`

### Issue: "Tesseract is not installed"
**Solution:** Install Tesseract OCR (see Step 2 above)
- On Windows, make sure you installed it from the correct link
- On macOS/Linux, run the brew/apt-get commands above

### Issue: "GROQ_API_KEY not found"
**Solution:** Create the `.env` file (Step 6) with your actual Groq API key

### Issue: "Port 5000 already in use"
**Solution:** Change the port in the app. Open `app.py` and modify the uvicorn.run() call:
```python
uvicorn.run(app, host="127.0.0.1", port=8000)  # Changed from 5000
```

### Issue: "Database file not created"
**Solution:** The database is created automatically on first run. Wait a few seconds after starting the server.

---

## Project Structure

```
├── app.py                     # Main FastAPI application
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create this)
├── database/
│   └── models.py             # Database models
├── services/
│   ├── file_processor.py     # PDF/DOCX/Image parsing
│   ├── groq_parser.py        # Groq API integration
│   ├── llm_parser.py         # LLM parsing wrapper
│   └── search_engine.py      # Candidate search logic
├── static/
│   ├── script.js             # Frontend JavaScript
│   └── style.css             # Frontend styling
├── templates/
│   └── index.html            # Main HTML interface
├── utils/
│   ├── helpers.py            # Utility functions
│   └── validation.py         # Input validation
├── uploads/                  # Resume storage (created automatically)
└── resume_parser.db          # SQLite database (created automatically)
```

---

## Features You Can Use

### 1. Upload Resumes
- Drag and drop or click to browse
- Supports: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG

### 2. Search by Skills
- Type any skill (e.g., "Python", "React.js", "MongoDB")
- Results show candidates with matching skills

### 3. Search by Job Role
- Type any job role (e.g., "MERN Stack Developer", "Data Scientist")
- Shows candidates ranked by skill match percentage

### Available Job Roles:
- MERN Stack Developer
- Full Stack Developer
- Frontend Developer
- Backend Developer
- Data Scientist
- DevOps Engineer
- Mobile Developer
- UI/UX Designer
- Cloud Architect
- QA Engineer

### 4. View Resumes
- Select a resume from the dropdown
- View the PDF in the Document Viewer
- See extracted information (name, skills, experience, education)

---

## Development Tips

### Testing the Groq API
```bash
python test_groq.py
```

### Viewing Database Contents
```bash
python view_database.py
```

### Checking Available Groq Models
```bash
python check_groq_models.py
```

---

## Stop the Server

Press `Ctrl+C` in your terminal to stop the server.

---

## Next Steps

1. **Upload some resumes** to build your candidate database
2. **Test job role search** to find suitable candidates
3. **View extracted information** to verify accuracy
4. **Customize job roles** by editing `job_roles.json`

---

## Support

For issues with:
- **Groq API**: Visit https://console.groq.com/docs
- **FastAPI**: Visit https://fastapi.tiangolo.com/
- **This Project**: Check the replit.md file for more information

Enjoy using the AI Resume Screening System! 🚀
