from database.models import SessionLocal, Candidate, Skill, Education, Experience, Project

def view_database():
    db = SessionLocal()
    try:
        print("=== CANDIDATES ===")
        candidates = db.query(Candidate).all()
        
        for candidate in candidates:
            print(f"\nID: {candidate.id}, Name: {candidate.name}, Email: {candidate.email}")
            print(f"Phone: {candidate.phone}, Location: {candidate.location}")
            print(f"Skills: {[skill.name for skill in candidate.skills]}")
            print("Education:")
            for edu in candidate.education:
                print(f"  - {edu.degree} at {edu.institution} ({edu.year})")
            print("Experience:")
            for exp in candidate.experiences:
                print(f"  - {exp.job_title} @ {exp.company} ({exp.duration})")
            print("Projects:")
            for proj in candidate.projects:
                print(f"  - {proj.title} ({proj.duration}) | Tech: {proj.technologies_used}")
            
            print("---")
        
        print("\n=== SKILLS ===")
        skills = db.query(Skill).all()
        for skill in skills:
            print(f"ID: {skill.id}, Name: {skill.name}, Category: {skill.category}")
        
        print("\n=== PROJECTS TABLE ===")
        all_projects = db.query(Project).all()
        for proj in all_projects:
            print(f"ID: {proj.id}, Title: {proj.title}, CandidateID: {proj.candidate_id}")

        print(f"\nTotal Candidates: {len(candidates)}")
        print(f"Total Skills: {len(skills)}")
        print(f"Total Projects: {len(all_projects)}")

    finally:
        db.close()

if __name__ == "__main__":
    view_database()
