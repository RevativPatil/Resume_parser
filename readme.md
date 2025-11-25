# AI Resume Screening System

An intelligent resume parsing and screening system built with FastAPI and Groq's ultra-fast LLM API. This application automatically extracts structured information from resumes in multiple formats and provides AI-powered skill-based candidate search with job role matching.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 Features

- **Multi-format Resume Support**: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
- **AI-Powered Entity Extraction**: Uses Groq's Llama 3.3 70B model for intelligent data extraction
- **Smart Skill-Based Search**: Fuzzy matching with synonym support
- **Job Role Matching**: 10 pre-built job roles with percentage-based candidate ranking
- **Resume Document Viewer**: View parsed resumes directly in the browser
- **Extracted Information Display**: Name, skills, education, experience, location
- **High Performance**: Groq API provides 200-300 tokens/second
- **Modern Web UI**: Clean, responsive interface for HR teams

## 🏗️ Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **LLM Provider**: Groq API (llama-3.3-70b-versatile)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy
- **OCR**: Tesseract (for image-based resumes)
- **PDF Parsing**: pdfplumber
- **Document Parsing**: python-docx

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Responsive design
- **JavaScript**: Vanilla JS (no frameworks)
- **Icons**: FontAwesome

## 📁 Project Structure

```
ai-resume-screening/
├── app.py                          # Main FastAPI application
├── config.py                       # Configuration and settings
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── SETUP_LOCAL.md                 # Local setup guide
├── job_roles.json                 # Pre-defined job roles
├── resume_parser.db               # SQLite database (auto-created)
│
├── database/
│   ├── __init__.py
│   └── models.py                  # SQLAlchemy models
│
├── services/
│   ├── file_processor.py          # PDF/DOCX/Image parsing
│   ├── groq_parser.py             # Groq API integration
│   ├── llm_parser.py              # LLM parsing orchestration
│   └── search_engine.py           # Candidate search & job role matching
│
├── static/
│   ├── script.js                  # Frontend JavaScript
│   └── style.css                  # Frontend styling
│
├── templates/
│   └── index.html                 # Main web interface
│
├── utils/
│   ├── helpers.py                 # Utility functions
│   ├── validation.py              # Input validation
│
└── uploads/                       # Resume file storage (auto-created)
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- pip (Python package manager)
- Tesseract OCR (for image parsing)
- Groq API key (free: https://console.groq.com)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-resume-screening
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   - **Windows**: https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

5. **Create `.env` file**
   ```env
   GROQ_API_KEY=your-groq-api-key-here
   DATABASE_URL=sqlite:///./resume_parser.db
   GROQ_MODEL=llama-3.3-70b-versatile
   DEBUG=True
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open in browser**
   ```
   http://localhost:5000
   ```

---

## 🗄️ Database Configuration

### Option 1: SQLite (Development - Default)

SQLite is pre-configured for local development. No additional setup required.

**Configuration:**
```env
DATABASE_URL=sqlite:///./resume_parser.db
```

**Features:**
- ✅ Zero setup - works immediately
- ✅ File-based (easy to backup)
- ✅ Perfect for development and testing
- ✅ ~5MB database file size

**Database Tables:**
```sql
candidates
├── id (INTEGER PRIMARY KEY)
├── name (VARCHAR)
├── email (VARCHAR)
├── phone (VARCHAR)
├── location (VARCHAR)
├── experience_summary (TEXT)
├── raw_text (TEXT)
├── resume_file_path (VARCHAR)
├── created_at (DATETIME)

skills
├── id (INTEGER PRIMARY KEY)
├── candidate_id (INTEGER FOREIGN KEY)
├── name (VARCHAR)
├── category (VARCHAR)

education
├── id (INTEGER PRIMARY KEY)
├── candidate_id (INTEGER FOREIGN KEY)
├── degree (VARCHAR)
├── institution (VARCHAR)
├── field_of_study (VARCHAR)
├── graduation_year (INTEGER)

experience
├── id (INTEGER PRIMARY KEY)
├── candidate_id (INTEGER FOREIGN KEY)
├── job_title (VARCHAR)
├── company (VARCHAR)
├── duration (VARCHAR)
├── description (TEXT)
```

**View SQLite Database:**

Option A - Command Line:
```bash
sqlite3 resume_parser.db
sqlite> .tables
sqlite> SELECT * FROM candidates;
sqlite> .exit
```

Option B - GUI Tool:
- Download DB Browser for SQLite: https://sqlitebrowser.org/
- Open `resume_parser.db` and browse visually

Option C - Python Script:
```bash
python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('resume_parser.db')
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM candidates")
print(f"Total candidates: {cursor.fetchone()[0]}")
conn.close()
EOF
```

---

### Option 2: PostgreSQL (Production)

For production deployments, use PostgreSQL for better performance and scalability.

**Prerequisites:**
- PostgreSQL 12+ installed
- psycopg2-binary (already in requirements.txt)

**Installation Steps:**

1. **Install PostgreSQL**
   - **Windows**: https://www.postgresql.org/download/windows/
   - **macOS**: `brew install postgresql`
   - **Linux**: `sudo apt-get install postgresql postgresql-contrib`

2. **Create Database and User**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Inside psql:
   CREATE DATABASE resume_parser;
   CREATE USER resume_user WITH PASSWORD 'your-secure-password';
   ALTER ROLE resume_user SET client_encoding TO 'utf8';
   ALTER ROLE resume_user SET default_transaction_isolation TO 'read committed';
   ALTER ROLE resume_user SET default_transaction_deferrable TO on;
   ALTER ROLE resume_user SET default_transaction_read_committed TO off;
   ALTER ROLE resume_user SET timezone TO 'UTC';
   GRANT ALL PRIVILEGES ON DATABASE resume_parser TO resume_user;
   \q
   ```

3. **Update `.env` file**
   ```env
   GROQ_API_KEY=your-groq-api-key-here
   DATABASE_URL=postgresql://resume_user:your-secure-password@localhost:5432/resume_parser
   GROQ_MODEL=llama-3.3-70b-versatile
   DEBUG=False
   ```

4. **Run migrations (if using Alembic)**
   ```bash
   alembic upgrade head
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

**Database Schema (PostgreSQL):**

The schema is identical to SQLite, but PostgreSQL provides:
- Better concurrent access
- ACID compliance
- Advanced indexing
- Connection pooling support
- Backup and replication capabilities

**View PostgreSQL Database:**

Option A - Command Line:
```bash
psql -U resume_user -d resume_parser
\dt                           # List tables
SELECT * FROM candidates;     # Query data
\q                            # Exit
```

Option B - GUI Tool:
- pgAdmin: https://www.pgadmin.org/
- DBeaver: https://dbeaver.io/

---

## 📊 Database Initialization

### Automatic Initialization (Both SQLite & PostgreSQL)

The database tables are automatically created on first application startup via SQLAlchemy:

```python
# In app.py
Base.metadata.create_all(bind=engine)
```

When you run `python app.py` for the first time:
1. SQLAlchemy checks for existing tables
2. Creates missing tables based on models.py
3. Ready to accept resume uploads

### Manual Database Reset (SQLite)

To clear all data and start fresh:

```bash
# Delete the database file
rm resume_parser.db

# Restart the app
python app.py
```

A fresh database will be created automatically.

### Manual Database Reset (PostgreSQL)

```bash
# Connect as admin
psql -U postgres

# Drop and recreate database
DROP DATABASE resume_parser;
CREATE DATABASE resume_parser;
GRANT ALL PRIVILEGES ON DATABASE resume_parser TO resume_user;
\q

# Run migrations (if using Alembic)
alembic upgrade head
```

---

## 🔍 Available Job Roles

The system includes 10 pre-built job roles for smart candidate matching:

1. **MERN Stack Developer** - React, Node.js, Express, MongoDB, etc.
2. **Full Stack Developer** - Frontend + Backend technologies
3. **Frontend Developer** - React, Vue, Angular, CSS, JavaScript
4. **Backend Developer** - Python, Node.js, Java, Go, APIs
5. **Data Scientist** - Python, SQL, Machine Learning, Statistics
6. **DevOps Engineer** - Docker, Kubernetes, CI/CD, Linux
7. **Mobile Developer** - React Native, Flutter, Swift, Kotlin
8. **UI/UX Designer** - Figma, Adobe XD, Prototyping, UX principles
9. **Cloud Architect** - AWS, Azure, GCP, Cloud Design
10. **QA Engineer** - Testing, Automation, Selenium, APIs

Each role has 12-18 specific required skills. Search by role name to find matching candidates!

---

## 🎮 How to Use

### 1. Upload Resumes
- Click "Upload Resume" section
- Drag and drop or click to browse
- Supported formats: PDF, DOCX, DOC, TXT, PNG, JPG, JPEG
- Max file size: 10MB

### 2. Search by Skills
- Enter any skill (e.g., "Python", "React.js", "AWS")
- Click Search
- Results show matching candidates with their extracted skills

### 3. Search by Job Role
- Enter any job role (e.g., "MERN Stack Developer")
- Click Search
- Results show candidates ranked by skill match percentage
- 🟢 Green (70%+): Excellent match
- 🟡 Orange (40-70%): Good match
- 🔴 Red (<40%): Partial match

### 4. View Candidate Details
- Select a resume from dropdown
- Click "Display Selected Resume"
- View PDF in Document Viewer
- See extracted information on the right

### 5. View Resume Files
- Download button in Document Viewer
- Open externally for verification

---

## 🔧 API Endpoints

### Resume Management
- `GET /` - Main web interface
- `GET /api/resumes` - List all candidates
- `GET /api/resume/{candidate_id}` - Get candidate details
- `GET /api/resume/file/{candidate_id}` - Download resume file
- `POST /api/upload-resume` - Upload and parse resume

### Search Endpoints
- `GET /api/search?q=<skill>` - Search by skill
- `GET /api/search-by-role?role=<role_name>` - Search by job role
- `GET /api/job-roles` - Get all available job roles

---

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Your Groq API key (required) |
| `DATABASE_URL` | `sqlite:///./resume_parser.db` | Database connection string |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | LLM model to use |
| `DEBUG` | `True` | Enable debug mode |

### Groq API

- **Free Tier**: 5,000 requests/day
- **Models Available**:
  - `llama-3.3-70b-versatile` (current, recommended)
  - `mixtral-8x7b-32768` (fastest, 32K context)
  - `llama2-70b-4096` (very capable)

Get your API key: https://console.groq.com/

---

## 🐛 Troubleshooting

### Database Issues

**Q: "No such table" error**
- A: Delete `resume_parser.db` and restart the app

**Q: PostgreSQL connection error**
- A: Verify DATABASE_URL and ensure PostgreSQL service is running

**Q: How to switch from SQLite to PostgreSQL?**
- A: Update DATABASE_URL in `.env` and restart the app

### File Upload Issues

**Q: "Tesseract is not installed" error**
- A: Install Tesseract OCR (see Installation section)

**Q: "File type not supported"**
- A: Only PDF, DOCX, DOC, TXT, PNG, JPG, JPEG are supported

**Q: File upload hangs**
- A: Check file size (max 10MB) and internet connection for Groq API

### API Issues

**Q: "GROQ_API_KEY not found"**
- A: Create `.env` file with your API key

**Q: "Rate limit exceeded"**
- A: You've exceeded 5,000 requests/day. Try again tomorrow or upgrade plan.

---

## 📈 Performance Tips

1. **Use PostgreSQL for production** - Better performance with multiple users
2. **Enable HTTP caching** - Already configured in app
3. **Optimize PDF parsing** - Use high-quality resumes
4. **Batch uploads** - Upload multiple resumes together when possible
5. **Index frequently searched skills** - Improve query performance

---

## 🚀 Deployment

### Deploy to Replit

1. Push code to Replit
2. Configure environment variables in Secrets tab
3. Click "Deploy" button
4. Choose "Autoscale" for automatic scaling

### Deploy Locally with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Deploy with Docker

```bash
docker build -t resume-parser .
docker run -p 5000:5000 -e GROQ_API_KEY=<your-key> resume-parser
```

---

## 📝 Example Workflow

1. **Admin opens the application**
   ```
   http://localhost:5000
   ```

2. **Uploads 10 candidate resumes**
   - System extracts skills, education, experience automatically

3. **Searches for "MERN Stack Developer"**
   - System shows 7 candidates ranked by skill match
   - Match percentages: 80%, 65%, 55%, 45%, 35%, 25%, 15%

4. **Clicks on top candidate**
   - Views resume PDF
   - Sees extracted information

5. **Interviews candidate and hires them**
   - Can mark candidate as hired in future versions

---

## 📊 Current Database Status

When you run the app, you get a pre-populated database with:
- **8 Sample Candidates** (ready to search)
- **123 Skills** extracted from resumes
- **16 Education Records** from various candidates

Try searching for: "MERN Stack", "Python", "React" to see results!

---

## 🔐 Security Notes

- API keys stored securely in `.env` (not in code)
- Never commit `.env` file to version control
- Database passwords for PostgreSQL should be strong
- File uploads validated and stored in `uploads/` directory
- SQL injection prevented via SQLAlchemy ORM

---

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Groq API Docs**: https://console.groq.com/docs
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **PostgreSQL Docs**: https://www.postgresql.org/docs/
- **Tesseract OCR**: https://github.com/UB-Mannheim/tesseract/wiki

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🎯 Future Enhancements

- [ ] Advanced search filters (location, salary, experience)
- [ ] Resume comparison feature
- [ ] Email notifications for new candidates
- [ ] Batch upload with progress tracking
- [ ] Export to CSV/Excel
- [ ] Custom job role creation
- [ ] Candidate rating and feedback
- [ ] Interview scheduling integration
- [ ] Machine learning-based smart matching
- [ ] Multi-language resume support

---

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub or contact the development team.

---

**Made with ❤️ for HR Teams**
