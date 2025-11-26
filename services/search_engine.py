from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Dict, Any
from database.models import Candidate, Skill, Education, Experience
import re
import json
import os

class SearchEngine:
    def __init__(self, db: Session):
        self.db = db
        self.job_roles = self._load_job_roles()
    
    def _load_job_roles(self) -> Dict:
        """Load job roles from job_roles.json file"""
        try:
            job_roles_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'job_roles.json')
            with open(job_roles_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}
    
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
            
            # Filter: Only include candidates with at least 70% match
            if match_percentage >= 70:
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
    
    def _normalize_skill(self, skill: str) -> str:
        """Normalize skill name for accurate matching"""
        normalized = skill.lower().strip()
        normalized = re.sub(r'[.\-_\s]+', '', normalized)
        return normalized
    
    def _skills_match(self, required_skill: str, candidate_skill: str) -> bool:
        """Check if two skills match using intelligent matching logic"""
        normalized_required = self._normalize_skill(required_skill)
        normalized_candidate = self._normalize_skill(candidate_skill)
        
        if normalized_required == normalized_candidate:
            return True
        
        skill_synonyms = {
            'javascript': ['javascript', 'js'],
            'typescript': ['typescript', 'ts'],
            'mongodb': ['mongodb', 'mongo'],
            'nodejs': ['node', 'nodejs'],
            'reactjs': ['react', 'reactjs'],
            'react': ['react', 'reactjs'],
            'nextjs': ['next', 'nextjs'],
            'next': ['next', 'nextjs'],
            'expressjs': ['express', 'expressjs'],
            'express': ['express', 'expressjs'],
            'git': ['git', 'github', 'gitlab'],
            'github': ['git', 'github', 'gitlab'],
            'gitlab': ['git', 'github', 'gitlab'],
            'aws': ['aws', 'amazonwebservices'],
            'amazonwebservices': ['aws', 'amazonwebservices'],
            'azure': ['azure', 'microsoftazure'],
            'microsoftazure': ['azure', 'microsoftazure'],
            'gcp': ['gcp', 'googlecloudplatform', 'googlecloud'],
            'googlecloudplatform': ['gcp', 'googlecloudplatform', 'googlecloud'],
            'googlecloud': ['gcp', 'googlecloudplatform', 'googlecloud'],
            'c': ['c', 'clang', 'cprogramming'],
            'cpp': ['cpp', 'c++', 'cplusplus'],
            'c++': ['cpp', 'c++', 'cplusplus'],
            'csharp': ['csharp', 'c#'],
            'c#': ['csharp', 'c#'],
            'r': ['r', 'rprogramming', 'rlanguage'],
            'go': ['go', 'golang'],
            'golang': ['go', 'golang'],
        }
        
        for skill_key, synonyms in skill_synonyms.items():
            if normalized_required in synonyms and normalized_candidate in synonyms:
                return True
        
        if normalized_required in normalized_candidate:
            required_len = len(normalized_required)
            candidate_len = len(normalized_candidate)
            
            if required_len >= 4 and (normalized_candidate.startswith(normalized_required) or normalized_candidate.endswith(normalized_required)):
                return True
            
            if required_len >= 5:
                ratio = required_len / candidate_len
                if ratio >= 0.6:
                    return True
        
        if normalized_candidate in normalized_required:
            candidate_len = len(normalized_candidate)
            required_len = len(normalized_required)
            if candidate_len >= 4 and (candidate_len / required_len) >= 0.75:
                return True
        
        return False
    
    def search_by_job_role(self, job_role_key: str) -> Dict[str, Any]:
        """Search candidates by job role and rank by skill match percentage"""
        job_role_key = job_role_key.lower().replace(' ', '_').replace('-', '_')
        
        if job_role_key not in self.job_roles:
            return {
                "success": False,
                "message": f"Job role '{job_role_key}' not found",
                "available_roles": list(self.job_roles.keys())
            }
        
        job_role = self.job_roles[job_role_key]
        required_skills = job_role['skills']
        
        all_candidates = self.db.query(Candidate).all()
        
        results = []
        for candidate in all_candidates:
            candidate_skills = [skill.name for skill in candidate.skills]
            
            matched_skills = []
            missing_skills = []
            
            for required_skill in required_skills:
                skill_matched = False
                for candidate_skill in candidate_skills:
                    if self._skills_match(required_skill, candidate_skill):
                        matched_skills.append(required_skill)
                        skill_matched = True
                        break
                
                if not skill_matched:
                    missing_skills.append(required_skill)
            
            match_count = len(matched_skills)
            total_required = len(required_skills)
            match_percentage = int((match_count / total_required) * 100) if total_required > 0 else 0
            
            # Filter: Only include candidates with at least 70% match
            if match_percentage >= 70:
                results.append({
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "location": candidate.location,
                    "experience_summary": candidate.experience_summary,
                    "match_percentage": match_percentage,
                    "matched_skills": matched_skills,
                    "missing_skills": missing_skills,
                    "matched_count": match_count,
                    "total_required": total_required,
                    "all_candidate_skills": candidate_skills
                })
        
        results.sort(key=lambda x: x["match_percentage"], reverse=True)
        
        return {
            "success": True,
            "job_role": job_role['title'],
            "required_skills": job_role['skills'],
            "total_candidates": len(results),
            "candidates": results
        }
    
    def get_available_job_roles(self) -> List[Dict[str, str]]:
        """Get list of all available job roles"""
        return [
            {
                "key": key,
                "title": role['title'],
                "skills_count": len(role['skills'])
            }
            for key, role in self.job_roles.items()
        ]