from services.groq_parser import GroqResumeParser
import os

def test_groq_integration():
    """Test Groq API integration"""
    print(" Testing Groq API Integration...")
    
    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print(" GROQ_API_KEY not found in environment variables")
        print(" Get your free API key from: https://console.groq.com/")
        print(" Then set it: export GROQ_API_KEY=your_key_here")
        return
    
    try:
        # Test parser initialization
        parser = GroqResumeParser()
        
        # Test connection
        if parser.test_connection():
            print(" Groq API connection successful!")
        else:
            print(" Groq API connection failed")
            return
        
        # Test with sample resume
        sample_resume = """
        Johnathan Smith
        john.smith@tech.com | (415) 555-1234 | San Francisco, CA
        LinkedIn: linkedin.com/in/johnsmith | GitHub: github.com/johnsmith
        
        TECHNICAL SKILLS
        Programming: Python, JavaScript, TypeScript, Java, SQL
        Frameworks: React, Node.js, Django, Spring Boot, Express.js
        Cloud & DevOps: AWS, Docker, Kubernetes, Jenkins, Terraform
        Databases: PostgreSQL, MongoDB, Redis, MySQL
        
        EXPERIENCE
        Senior Software Engineer - Google Cloud (2021-Present)
        - Developed scalable microservices using Python and React
        - Led migration of legacy systems to Kubernetes on AWS
        - Implemented CI/CD pipelines using Jenkins and Docker
        
       
        PROJECTS EXTRACTION RULE:
       - If the resume does NOT explicitly contain a "Projects" section, 
         extract project-like content from job experience.
       - Identify bullet points or sentences describing a specific product/application.
       - Include project name (if not available, generate a short meaningful title).


        Software Engineer - Microsoft (2019-2021) 
        - Built full-stack applications with TypeScript and Node.js
        - Designed and implemented RESTful APIs
        - Collaborated with cross-functional teams using Agile
        
        EDUCATION
        Master of Science in Computer Science - Stanford University (2019)
        Bachelor of Science in Software Engineering - UC Berkeley (2017)
        """
        
        print("\n Testing resume parsing...")
        result = parser.parse_resume(sample_resume)

        print(" Parsing Results:")
        print(f"Name: {result.get('name', 'Not found')}")
        print(f"Email: {result.get('email', 'Not found')}")
        print(f"Phone: {result.get('phone', 'Not found')}")
        print(f"Skills: {', '.join(result.get('skills', []))}")
        print(f"Experience entries: {len(result.get('experience', []))}")
        print(f"Education entries: {len(result.get('education', []))}")
        print(f"Project entries: {len(result.get('projects', []))}")  # 👈 New line

        
    except Exception as e:
        print(f" Test failed: {e}")

if __name__ == "__main__":
    test_groq_integration()