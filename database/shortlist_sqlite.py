import sqlite3
import json
from typing import List, Dict, Optional


class ShortlistedResumesDB:
    """SQLite database for storing shortlisted resumes with 70%+ match criteria"""
    
    def __init__(self, db_path: str = "shortlisted_resumes.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize the SQLite database with tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shortlisted_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL UNIQUE,
                candidate_name TEXT NOT NULL,
                skills TEXT NOT NULL,
                work_experience TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_shortlisted_resume(
        self,
        candidate_id: int,
        candidate_name: str,
        skills: List[str],
        work_experience: List[Dict],
        match_percentage: int
    ) -> Dict:
        """Add a shortlisted resume to the database if match_percentage >= 70%"""
        
        # Check if match percentage meets criteria
        if match_percentage < 70:
            return {
                "success": False,
                "message": f"Match percentage {match_percentage}% is below 70% threshold",
                "added_to_sqlite": False
            }
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if already exists
            cursor.execute(
                "SELECT id FROM shortlisted_candidates WHERE candidate_id = ?",
                (candidate_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                return {
                    "success": True,
                    "message": "Candidate already in shortlist",
                    "id": existing[0],
                    "added_to_sqlite": False
                }
            
            # Convert lists to JSON
            skills_json = json.dumps(skills)
            experience_json = json.dumps(work_experience)
            
            cursor.execute('''
                INSERT INTO shortlisted_candidates 
                (candidate_id, candidate_name, skills, work_experience)
                VALUES (?, ?, ?, ?)
            ''', (candidate_id, candidate_name, skills_json, experience_json))
            
            conn.commit()
            record_id = cursor.lastrowid
            
            return {
                "success": True,
                "message": f"Successfully added {candidate_name} to shortlist (Match: {match_percentage}%)",
                "id": record_id,
                "added_to_sqlite": True
            }
        
        except Exception as e:
            conn.rollback()
            return {
                "success": False,
                "message": f"Error adding to shortlist: {str(e)}",
                "added_to_sqlite": False
            }
        finally:
            conn.close()
    
    def get_all_shortlisted(self) -> List[Dict]:
        """Get all shortlisted resumes with candidate name, skills, and work experience"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM shortlisted_candidates')
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                results.append({
                    "id": row[0],
                    "candidate_id": row[1],
                    "candidate_name": row[2],
                    "skills": json.loads(row[3]),
                    "work_experience": json.loads(row[4])
                })
            
            return results
        finally:
            conn.close()
    
    def remove_shortlisted(self, record_id: int) -> Dict:
        """Remove a shortlisted resume"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT candidate_name FROM shortlisted_candidates WHERE id = ?',
                (record_id,)
            )
            row = cursor.fetchone()
            
            if not row:
                return {
                    "success": False,
                    "message": "Record not found"
                }
            
            candidate_name = row[0]
            cursor.execute('DELETE FROM shortlisted_candidates WHERE id = ?', (record_id,))
            conn.commit()
            
            return {
                "success": True,
                "message": f"Removed {candidate_name} from shortlist"
            }
        finally:
            conn.close()
