import os
import json
import re
from groq import Groq
from typing import Dict, Any, List
from config import settings

class GroqResumeParser:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required. Get it from https://console.groq.com/")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        
        # Available Groq models
        self.available_models = {
            "mixtral": "mixtral-8x7b-32768",  # Fastest, 32K context
            "llama70b": "llama2-70b-4096",     # Very capable
            "gemma": "gemma-7b-it"            # New, efficient
        }
        
        print(f" Groq parser initialized with model: {self.model}")

    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Parse resume text using Groq API"""
        
        prompt = self._create_parsing_prompt(text)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert resume parser. Extract structured information and return ONLY valid JSON."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=2000,
                top_p=0.9
            )
            
            result_text = response.choices[0].message.content
            return self._extract_and_validate_json(result_text)
            
        except Exception as e:
            print(f" Groq API error: {str(e)}")
            return self._get_fallback_response(text)

    def _create_parsing_prompt(self, text: str) -> str:
        """Create optimized prompt for resume parsing with Groq"""
        return f"""
        Extract structured information from this resume text. Be accurate and precise.

        RESUME TEXT:
        {text[:12000]}

        Extract these entities:
        - name: Full name (only if clearly identified at top)
        - email: Email address using regex pattern
        - phone: Phone number in any format
        - location: City/State/Country if mentioned
        - skills: List of ALL technical skills, programming languages, tools, frameworks
        - education: List of education entries with degree, institution, year, field_of_study
        - experience: List of work experiences with job_title, company, duration, description, start_date, end_date
        - experience_summary: Brief 1-2 line summary of total experience

        IMPORTANT RULES:
        1. For name: Only extract if it's clearly the candidate's name at the beginning
        2. For skills: Include ALL technologies mentioned, even in experience descriptions
        3. For education: Extract degree, institution, and year separately
        4. For experience: Be thorough with job titles and companies

        Return ONLY valid JSON with this exact structure:
        {{
            "name": "string",
            "email": "string",
            "phone": "string",
            "location": "string", 
            "skills": ["string"],
            "education": [
                {{
                    "degree": "string",
                    "institution": "string",
                    "year": "string",
                    "field_of_study": "string"
                }}
            ],
            "experience": [
                {{
                    "job_title": "string",
                    "company": "string",
                    "duration": "string",
                    "description": "string",
                    "start_date": "string", 
                    "end_date": "string"
                }}
            ],
            "experience_summary": "string"

            "projects": [
               {{
                   "title": "RAG Chatbot for Internal Knowledge Search",
                   "description": "Built a Generative AI chatbot using LangChain, FAISS... ",
                   "technologies_used": "LangChain, FastAPI, FAISS, Azure OpenAI",
                   "github_link": "",
                   "role": "Developer",
                   "duration": "June 2023 - Present"
               }}
]

        }}

        If you cannot find certain information, use empty strings or empty arrays.
        """

    def _extract_and_validate_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Groq response and validate structure"""
        try:
            # Clean the response and find JSON
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed_data = json.loads(json_str)
                return self._validate_parsed_data(parsed_data)
            else:
                print(" No JSON found in response")
                return self._get_empty_structure()
                
        except json.JSONDecodeError as e:
            print(f" JSON decode error: {e}")
            return self._get_empty_structure()
        except Exception as e:
            print(f" Validation error: {e}")
            return self._get_empty_structure()

    def _validate_parsed_data(self, data: Dict) -> Dict:
        """Validate and clean the parsed data"""
        # Ensure all required fields exist
        required_fields = {
            'name': '',
            'email': '', 
            'phone': '',
            'location': '',
            'skills': [],
            'education': [],
            'experience': [],
            'experience_summary': '',
            'projects': []
        }
        
        for field, default in required_fields.items():
            if field not in data:
                data[field] = default
        
        # Validate types
        if not isinstance(data['skills'], list):
            data['skills'] = []
        if not isinstance(data['education'], list):
            data['education'] = []
        if not isinstance(data['experience'], list):
            data['experience'] = []
        if not isinstance(data['projects'], list):
            data['projects'] = []
            
        # Clean skills - remove empty strings, duplicates
        data['skills'] = [skill for skill in data['skills'] if skill and isinstance(skill, str)]
        data['skills'] = list(set(data['skills']))  # Remove duplicates
        
        return data

    def _get_empty_structure(self) -> Dict[str, Any]:
        """Return empty structure when parsing fails"""
        return {
            "name": "",
            "email": "", 
            "phone": "",
            "location": "",
            "skills": [],
            "education": [],
            "experience": [],
            "experience_summary": "",
            "projects": []
        }

    def _get_fallback_response(self, text: str) -> Dict[str, Any]:
        """Fallback method if Groq API fails"""
        print(" Using fallback parsing...")
        
        # Simple regex-based fallback
        result = self._get_empty_structure()
        
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            result['email'] = email_match.group()
            
        # Extract phone
        phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            result['phone'] = phone_match.group()
            
        # Simple skill extraction
        common_skills = self._get_common_skills()
        found_skills = []
        for skill in common_skills:
            if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE):
                found_skills.append(skill)
        result['skills'] = found_skills
        
        return result

    def _get_common_skills(self) -> List[str]:
        """List of common IT skills for fallback extraction"""
        return [
            'python', 'java', 'javascript', 'typescript', 'react', 'angular', 'vue', 
            'node.js', 'express', 'django', 'flask', 'spring', 'fastapi',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
            'mysql', 'postgresql', 'mongodb', 'redis', 'sql',
            'git', 'jenkins', 'github', 'gitlab', 'ci/cd',
            'linux', 'unix', 'bash', 'shell', 'powershell',
            'html', 'css', 'sass', 'bootstrap', 'tailwind',
            'machine learning', 'ai', 'data science', 'pytorch', 'tensorflow'
        ]

    def test_connection(self) -> bool:
        """Test Groq API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Say 'OK' if working."}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f" Groq connection test failed: {e}")
            return False