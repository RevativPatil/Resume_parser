from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from sqlalchemy.orm import Session
import os
import shutil
from typing import List, Optional

from config import settings
from database.models import Base, engine, Candidate, Skill, Education, Experience, SessionLocal
from services.file_processor import FileProcessor
from services.llm_parser import LLMResumeParser
from services.search_engine import SearchEngine
from utils.helpers import get_db

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Resume Screening", debug=settings.DEBUG)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure upload directory exists
os.makedirs("uploads", exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """SUBMIT resume file"""
    try:
        # Validate file
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not supported")
        
        # Save file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text
        file_processor = FileProcessor()
        raw_text = file_processor.extract_text_from_file(file_path, file_extension)
        cleaned_text = file_processor.clean_extracted_text(raw_text)
        
        if not cleaned_text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")
        
        # Parse with LLM
        llm_parser = LLMResumeParser()
        parsed_data = llm_parser.parse_resume(cleaned_text)
        
        # Save to database
        candidate = save_candidate_data(db, parsed_data, file_path, cleaned_text)
        
        return {
            "success": True,
            "candidate_id": candidate.id,
            "name": candidate.name,
            "message": "Resume parsed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_candidates(
    q: str,
    min_experience: Optional[int] = None,
    education: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Search candidates by skills and filters"""
    try:
        search_engine = SearchEngine(db)
        filters = {}
        
        if min_experience:
            filters['min_experience'] = min_experience
        if education:
            filters['education'] = education
            
        results = search_engine.search_candidates(q, filters)
        
        return {
            "success": True,
            "query": q,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resumes")
async def get_all_resumes(db: Session = Depends(get_db)):
    """Get all resume names for dropdown"""
    try:
        candidates = db.query(Candidate).all()
        return {
            "success": True,
            "resumes": [
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "filename": os.path.basename(c.resume_file_path) if c.resume_file_path else ""
                } for c in candidates
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resume/{candidate_id}")
async def get_resume_details(candidate_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific candidate"""
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return {
            "success": True,
            "candidate": {
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "phone": candidate.phone,
                "location": candidate.location,
                "experience_summary": candidate.experience_summary,
                "skills": [{"name": s.name, "category": s.category} for s in candidate.skills],
                "education": [
                    {
                        "degree": e.degree,
                        "institution": e.institution,
                        "year": e.year,
                        "field_of_study": e.field_of_study
                    } for e in candidate.education
                ],
                "experience": [
                    {
                        "job_title": e.job_title,
                        "company": e.company,
                        "duration": e.duration,
                        "description": e.description,
                        "start_date": e.start_date,
                        "end_date": e.end_date
                    } for e in candidate.experiences
                ],
                "resume_file_path": candidate.resume_file_path,
                "filename": os.path.basename(candidate.resume_file_path) if candidate.resume_file_path else ""
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resume/file/{candidate_id}")
async def get_resume_file(candidate_id: int, db: Session = Depends(get_db)):
    """Serve the resume file for viewing"""
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate or not candidate.resume_file_path:
            raise HTTPException(status_code=404, detail="Resume file not found")
        
        if not os.path.exists(candidate.resume_file_path):
            raise HTTPException(status_code=404, detail="Resume file not found on disk")
        
        file_extension = os.path.splitext(candidate.resume_file_path)[1].lower()
        
        media_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg'
        }
        
        media_type = media_types.get(file_extension, 'application/pdf')
        
        return FileResponse(
            candidate.resume_file_path,
            media_type=media_type,
            headers={
                "Content-Disposition": f'inline; filename="{os.path.basename(candidate.resume_file_path)}"',
                "Cache-Control": "no-cache"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/candidates")
async def get_all_candidates(db: Session = Depends(get_db)):
    """Get all parsed candidates"""
    try:
        candidates = db.query(Candidate).all()
        return {
            "success": True,
            "candidates": [
                {
                    "id": c.id,
                    "name": c.name,
                    "email": c.email,
                    "skills": [s.name for s in c.skills],
                    "experience_summary": c.experience_summary
                } for c in candidates
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/job-roles")
async def get_job_roles(db: Session = Depends(get_db)):
    """Get list of all available job roles"""
    try:
        search_engine = SearchEngine(db)
        roles = search_engine.get_available_job_roles()
        return {
            "success": True,
            "job_roles": roles
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search-by-role")
async def search_by_job_role(role: str, db: Session = Depends(get_db)):
    """Search candidates by job role and rank by skill match percentage"""
    try:
        search_engine = SearchEngine(db)
        result = search_engine.search_by_job_role(role)
        
        if not result.get("success", True):
            raise HTTPException(status_code=404, detail=result.get("message", "Job role not found"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/shortlisted")
async def get_shortlisted_candidates():
    """Get all shortlisted candidates from the separate shortlisted database"""
    try:
        from services.shortlisted_db import ShortlistedDatabase
        shortlisted_db = ShortlistedDatabase()
        candidates = shortlisted_db.get_all_shortlisted()
        return {
            "success": True,
            "count": len(candidates),
            "shortlisted_candidates": candidates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/shortlisted")
async def clear_shortlisted_candidates():
    """Clear all shortlisted candidates from the database"""
    try:
        from services.shortlisted_db import ShortlistedDatabase
        shortlisted_db = ShortlistedDatabase()
        shortlisted_db.clear_all()
        return {
            "success": True,
            "message": "All shortlisted candidates have been cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def save_candidate_data(db: Session, parsed_data: dict, file_path: str, raw_text: str) -> Candidate:
    """Save parsed candidate data to database"""
    
    # Create or update candidate
    candidate = db.query(Candidate).filter(Candidate.email == parsed_data['email']).first()
    if not candidate:
        candidate = Candidate(
            name=parsed_data.get('name', ''),
            email=parsed_data.get('email', ''),
            phone=parsed_data.get('phone', ''),
            location=parsed_data.get('location', ''),
            raw_text=raw_text,
            resume_file_path=file_path,
            experience_summary=parsed_data.get('experience_summary', '')
        )
        db.add(candidate)
        db.flush()
    
    # Process skills
    for skill_name in parsed_data.get('skills', []):
        if skill_name:
            skill = db.query(Skill).filter(Skill.normalized_name == skill_name.lower()).first()
            if not skill:
                skill = Skill(
                    name=skill_name,
                    normalized_name=skill_name.lower(),
                    category=categorize_skill(skill_name)
                )
                db.add(skill)
                db.flush()
            
            if skill not in candidate.skills:
                candidate.skills.append(skill)
    
    # Process education
    for edu_data in parsed_data.get('education', []):
        education = Education(
            candidate_id=candidate.id,
            degree=edu_data.get('degree', ''),
            institution=edu_data.get('institution', ''),
            year=edu_data.get('year', ''),
            field_of_study=edu_data.get('field_of_study', '')
        )
        db.add(education)
    
    # Process experience
    for exp_data in parsed_data.get('experience', []):
        experience = Experience(
            candidate_id=candidate.id,
            job_title=exp_data.get('job_title', ''),
            company=exp_data.get('company', ''),
            duration=exp_data.get('duration', ''),
            description=exp_data.get('description', ''),
            start_date=exp_data.get('start_date', ''),
            end_date=exp_data.get('end_date', '')
        )
        db.add(experience)
    
    db.commit()
    db.refresh(candidate)
    return candidate

def categorize_skill(skill_name: str) -> str:
    """Categorize skills into programming, tool, framework, or soft_skill"""
    skill_lower = skill_name.lower()
    
    programming_keywords = ['python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin']
    framework_keywords = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express']
    tool_keywords = ['docker', 'kubernetes', 'aws', 'azure', 'git', 'jenkins']
    
    if any(keyword in skill_lower for keyword in programming_keywords):
        return 'programming'
    elif any(keyword in skill_lower for keyword in framework_keywords):
        return 'framework'
    elif any(keyword in skill_lower for keyword in tool_keywords):
        return 'tool'
    else:
        return 'soft_skill'

if __name__ == "__main__":
    import uvicorn
    print(" Starting Resume Parser Server...")
    print(" Database URL:", settings.DATABASE_URL)
    print(" Groq Model:", settings.GROQ_MODEL)
    print(" Server will be available at: http://0.0.0.0:5000")
    uvicorn.run(app, host="0.0.0.0", port=5000, log_level="info")