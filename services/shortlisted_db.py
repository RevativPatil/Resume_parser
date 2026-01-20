import sqlite3
import os
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

class ShortlistedDatabase:
    MONTH_MAP = {
        'jan': 1, 'january': 1, 'feb': 2, 'february': 2, 'mar': 3, 'march': 3,
        'apr': 4, 'april': 4, 'may': 5, 'jun': 6, 'june': 6, 'jul': 7, 'july': 7,
        'aug': 8, 'august': 8, 'sep': 9, 'sept': 9, 'september': 9, 
        'oct': 10, 'october': 10, 'nov': 11, 'november': 11, 'dec': 12, 'december': 12
    }
    
    def __init__(self, db_path: str = "shortlisted_resumes.db"):
        self.db_path = db_path
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Create table if missing and add projects column if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shortlisted_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_name TEXT NOT NULL,
            work_experience_years REAL DEFAULT 0.0,
            skills TEXT NOT NULL,
            projects TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(candidate_name, skills, projects)
        )
        """)

        # Check if "projects" column exists; if missing, add it
        cursor.execute("PRAGMA table_info(shortlisted_candidates)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if "projects" not in columns:
            cursor.execute("ALTER TABLE shortlisted_candidates ADD COLUMN projects TEXT")

        conn.commit()
        conn.close()

    def _normalize_list(self, items: List[str]) -> str:
        """Normalize and convert list to comma-separated lowercase string"""
        if not items:
            return ""
        cleaned = sorted({i.lower().strip() for i in items if i and i.strip()})
        return ", ".join(cleaned)

    def _parse_date(self, date_str: str) -> Tuple[int, int]:
        """Extract month & year"""
        if not date_str:
            return (0, 0)

        date_str = date_str.lower().strip()
        
        if any(word in date_str for word in ["present", "current", "now"]):
            now = datetime.now()
            return now.year, now.month
        
        year = int(re.search(r'(\d{4})', date_str).group(1)) if re.search(r'(\d{4})', date_str) else 0
        
        month = next((num for name, num in self.MONTH_MAP.items() if name in date_str), 1)

        return (year, month)

    def _calculate_work_experience_years(self, experiences: List[Dict]) -> float:
        """Calculate work experience"""
        total_months = 0

        for exp in experiences:
            duration = exp.get("duration", "")
            if duration:
                years = int(re.search(r'(\d+)\s*year', duration, re.IGNORECASE).group(1)) if re.search(r'(\d+)\s*year', duration, re.IGNORECASE) else 0
                months = int(re.search(r'(\d+)\s*month', duration, re.IGNORECASE).group(1)) if re.search(r'(\d+)\s*month', duration, re.IGNORECASE) else 0
                total_months += years * 12 + months
                continue

            start_y, start_m = self._parse_date(exp.get("start_date", ""))
            end_y, end_m = self._parse_date(exp.get("end_date", "")) if exp.get("end_date") else (datetime.now().year, datetime.now().month)

            if start_y > 0:
                total_months += max(0, (end_y - start_y) * 12 + (end_m - start_m))

        return round(total_months / 12, 1)

    def store_shortlisted_candidate(self, candidate_name, experiences, skills, projects):
        """Save candidate with projects"""
        try:
            if not candidate_name:
                return False
            
            work_years = self._calculate_work_experience_years(experiences)
            skills_str = self._normalize_list(skills)
            projects_str = self._normalize_list(projects)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO shortlisted_candidates
                (candidate_name, work_experience_years, skills, projects)
                VALUES (?, ?, ?, ?)
            """, (candidate_name.strip(), work_years, skills_str, projects_str))

            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            print(f"Error storing shortlisted candidate: {e}")
            return False

    def store_multiple_candidates(self, candidates: List[Dict]) -> int:
        """Store many resumes"""
        count = 0
        for c in candidates:
            if self.store_shortlisted_candidate(
                c.get("name", ""), 
                c.get("experiences", []), 
                c.get("skills", []),
                c.get("projects", [])
            ):
                count += 1
        return count

    def get_all_shortlisted(self) -> List[Dict]:
        """Return all shortlisted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, candidate_name, work_experience_years, skills, projects, created_at 
            FROM shortlisted_candidates ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "candidate_name": row[1],
                "work_experience_years": row[2],
                "skills": row[3],
                "projects": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

    def clear_all(self):
        """Delete all rows"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shortlisted_candidates")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing shortlist: {e}")
            return False
