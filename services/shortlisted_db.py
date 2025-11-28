import sqlite3
import os
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime

class ShortlistedDatabase:
    MONTH_MAP = {
        'jan': 1, 'january': 1,
        'feb': 2, 'february': 2,
        'mar': 3, 'march': 3,
        'apr': 4, 'april': 4,
        'may': 5,
        'jun': 6, 'june': 6,
        'jul': 7, 'july': 7,
        'aug': 8, 'august': 8,
        'sep': 9, 'sept': 9, 'september': 9,
        'oct': 10, 'october': 10,
        'nov': 11, 'november': 11,
        'dec': 12, 'december': 12
    }
    
    def __init__(self, db_path: str = "shortlisted_resumes.db"):
        self.db_path = db_path
        self._create_table_if_not_exists()
    
    def _create_table_if_not_exists(self):
        """Create the shortlisted_candidates table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS shortlisted_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_name TEXT NOT NULL,
                work_experience_years REAL DEFAULT 0.0,
                skills TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(candidate_name, skills)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _normalize_skills(self, skills: List[str]) -> str:
        """Normalize and sort skills for consistent storage and deduplication"""
        if not skills:
            return ""
        normalized = [skill.strip().lower() for skill in skills if skill and skill.strip()]
        normalized = sorted(set(normalized))
        return ", ".join(normalized)
    
    def _parse_date(self, date_str: str) -> Tuple[int, int]:
        """Parse a date string and return (year, month) tuple"""
        if not date_str:
            return (0, 0)
        
        date_str = date_str.lower().strip()
        
        if 'present' in date_str or 'current' in date_str or 'now' in date_str:
            now = datetime.now()
            return (now.year, now.month)
        
        year = 0
        month = 1
        
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            year = int(year_match.group(1))
        
        for month_name, month_num in self.MONTH_MAP.items():
            if month_name in date_str:
                month = month_num
                break
        
        month_num_match = re.search(r'\b(\d{1,2})[/-]', date_str)
        if month_num_match:
            potential_month = int(month_num_match.group(1))
            if 1 <= potential_month <= 12:
                month = potential_month
        
        return (year, month)
    
    def _calculate_work_experience_years(self, experiences: List[Dict]) -> float:
        """Calculate total work experience in years from experience data"""
        total_months = 0
        
        for exp in experiences:
            duration = exp.get('duration', '')
            months_from_duration = 0
            
            if duration:
                years = 0
                months = 0
                
                year_match = re.search(r'(\d+)\s*(?:year|yr)s?', duration, re.IGNORECASE)
                if year_match:
                    years = int(year_match.group(1))
                
                month_match = re.search(r'(\d+)\s*(?:month|mo)s?', duration, re.IGNORECASE)
                if month_match:
                    months = int(month_match.group(1))
                
                months_from_duration = (years * 12) + months
            
            if months_from_duration > 0:
                total_months += months_from_duration
            else:
                start_date = exp.get('start_date', '')
                end_date = exp.get('end_date', '')
                
                if start_date:
                    start_year, start_month = self._parse_date(start_date)
                    
                    if end_date:
                        end_year, end_month = self._parse_date(end_date)
                    else:
                        now = datetime.now()
                        end_year, end_month = now.year, now.month
                    
                    if start_year > 0 and end_year > 0:
                        months_diff = (end_year - start_year) * 12 + (end_month - start_month)
                        if months_diff > 0:
                            total_months += months_diff
        
        return round(total_months / 12, 1) if total_months > 0 else 0.0
    
    def store_shortlisted_candidate(self, candidate_name: str, experiences: List[Dict], skills: List[str]) -> bool:
        """Store a shortlisted candidate in the database"""
        try:
            work_experience_years = self._calculate_work_experience_years(experiences)
            skills_str = self._normalize_skills(skills)
            candidate_name_normalized = candidate_name.strip() if candidate_name else ""
            
            if not candidate_name_normalized:
                return False
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR IGNORE INTO shortlisted_candidates 
                (candidate_name, work_experience_years, skills)
                VALUES (?, ?, ?)
            """, (candidate_name_normalized, work_experience_years, skills_str))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Error storing shortlisted candidate: {e}")
            return False
    
    def store_multiple_candidates(self, candidates: List[Dict]) -> int:
        """Store multiple shortlisted candidates at once"""
        stored_count = 0
        
        for candidate in candidates:
            name = candidate.get('name', '')
            experiences = candidate.get('experiences', [])
            skills = candidate.get('skills', [])
            
            if name:
                if self.store_shortlisted_candidate(name, experiences, skills):
                    stored_count += 1
        
        return stored_count
    
    def get_all_shortlisted(self) -> List[Dict]:
        """Get all shortlisted candidates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, candidate_name, work_experience_years, skills, created_at 
            FROM shortlisted_candidates
            ORDER BY created_at DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "id": row[0],
                "candidate_name": row[1],
                "work_experience_years": row[2],
                "skills": row[3],
                "created_at": row[4]
            }
            for row in rows
        ]
    
    def clear_all(self) -> bool:
        """Clear all shortlisted candidates"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shortlisted_candidates")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing shortlisted candidates: {e}")
            return False
