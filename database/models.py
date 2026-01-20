from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from config import settings

Base = declarative_base()

# Association table for candidate skills
candidate_skills = Table(
    'candidate_skills',
    Base.metadata,
    Column('candidate_id', ForeignKey('candidates.id')),
    Column('skill_id', ForeignKey('skills.id'))
)

class Candidate(Base):
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    location = Column(String)
    raw_text = Column(Text)
    resume_file_path = Column(String)
    experience_summary = Column(Text)
    match_percentage = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    skills = relationship("Skill", secondary=candidate_skills, back_populates="candidates")
    education = relationship("Education", back_populates="candidate")
    experiences = relationship("Experience", back_populates="candidate")
    projects = relationship("Project", back_populates="candidate")


class Skill(Base):
    __tablename__ = "skills"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    category = Column(String)  # programming, tool, framework, soft_skill
    normalized_name = Column(String, index=True)
    
    candidates = relationship("Candidate", secondary=candidate_skills, back_populates="skills")

class Education(Base):
    __tablename__ = "education"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    degree = Column(String)
    institution = Column(String)
    year = Column(String)
    field_of_study = Column(String)
    
    candidate = relationship("Candidate", back_populates="education")

class Experience(Base):
    __tablename__ = "experiences"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    job_title = Column(String)
    company = Column(String)
    duration = Column(String)
    description = Column(Text)
    start_date = Column(String)
    end_date = Column(String)
    
    candidate = relationship("Candidate", back_populates="experiences")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey('candidates.id'))
    title = Column(String)
    description = Column(Text)
    technologies_used = Column(String)  # comma-separated or JSON later
    github_link = Column(String)
    role = Column(String)
    duration = Column(String)
    
    candidate = relationship("Candidate", back_populates="projects")

# Create engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Base.metadata.create_all(bind=engine)