from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Dict, Any
from database.models import Candidate, Skill, Education, Experience
import re

class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def search_candidates(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """Search candidates based on skills and other criteria"""
        if filters is None:
            filters = {}
        
        # Base query
        base_query = self.db.query(Candidate)
        
        # Skill-based search
        if query:
            skill_terms = self._parse_search_query(query)
            base_query = self._apply_skill_search(base_query, skill_terms)
        
        # Apply filters
        base_query = self._apply_filters(base_query, filters)
        
        # Execute query
        candidates = base_query.all()
        
        # Calculate match percentages
        results = []
        for candidate in candidates:
            match_percentage = self._calculate_match_percentage(candidate, skill_terms if query else [])
            results.append({
                "id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "key_skills": [skill.name for skill in candidate.skills[:10]],
                "experience_summary": candidate.experience_summary,
                "match_percentage": match_percentage,
                "resume_file_path": candidate.resume_file_path
            })
        
        # Sort by match percentage
        results.sort(key=lambda x: x["match_percentage"], reverse=True)
        return results
    
    def _parse_search_query(self, query: str) -> List[str]:
        """Parse search query into individual skill terms"""
        # Split by commas, spaces, and common separators
        terms = re.split(r'[,+\s]+', query.lower())
        return [term.strip() for term in terms if term.strip()]
    
    def _apply_skill_search(self, query, skill_terms: List[str]):
        """Apply skill-based search to the query"""
        from sqlalchemy import func
        
        if not skill_terms:
            return query
        
        # Build OR conditions for all skill terms
        skill_filters = []
        for term in skill_terms:
            skill_filters.append(
                or_(
                    func.lower(Skill.name).like(f"%{term}%"),
                    func.lower(Skill.normalized_name).like(f"%{term}%")
                )
            )
        
        # Join and apply OR filter
        query = query.join(Candidate.skills).filter(or_(*skill_filters))
        
        return query.distinct()
    
    def _apply_filters(self, query, filters: Dict):
        """Apply additional filters like experience, education, etc."""
        if filters.get('min_experience'):
            # This would need more sophisticated experience parsing
            pass
        
        if filters.get('education'):
            query = query.join(Candidate.education).filter(
                func.lower(Education.degree).like(f"%{filters['education']}%")
            )
        
        return query
    
    def _calculate_match_percentage(self, candidate, search_terms: List[str]) -> int:
        """Calculate match percentage between candidate and search terms"""
        if not search_terms:
            return 0
        
        candidate_skills = [skill.normalized_name.lower() for skill in candidate.skills]
        matched_skills = 0
        
        for term in search_terms:
            if any(term in skill for skill in candidate_skills):
                matched_skills += 1
        
        return int((matched_skills / len(search_terms)) * 100)