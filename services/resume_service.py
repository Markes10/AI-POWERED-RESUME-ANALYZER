"""
Resume service for handling resume-related operations
"""
from typing import Dict, List, Optional
from db.database import DatabaseOperations
from services.embedding_service import embed_text, calculate_similarity
from services.skill_extractor import extract_skills
from services.language_utils import detect_language

class ResumeService(DatabaseOperations):
    def __init__(self):
        super().__init__('resumes')

    def create_resume(self, user_id: int, tenant_id: int, resume_text: str) -> Dict:
        """Create a new resume entry"""
        if user_id is None:
            raise ValueError("user_id is required")
        if tenant_id is None:
            raise ValueError("tenant_id is required")
        if not resume_text or not resume_text.strip():
            raise ValueError("resume_text is required")

        # Extract skills and generate embedding
        try:
            lang = detect_language(resume_text)
        except Exception:
            lang = None
        skills = extract_skills(resume_text, lang=lang)
        vector = embed_text(resume_text)
        
        # Convert vector to string for storage
        import json
        vector_str = json.dumps(vector)
        
        # Prepare data for insertion
        data = {
            'tenant_id': tenant_id,
            'user_id': user_id,
            'resume_text': resume_text,
            'skills': skills,
            'vector_embedding': vector_str
        }
        
        # Insert into database
        resume_id = self.create(data)
        result = self.get_by_id(resume_id)
        return result if result else {}

    def get_user_resumes(self, user_id: int, tenant_id: int) -> List[Dict]:
        """Get all resumes for a user"""
        query = "SELECT * FROM resumes WHERE user_id = %s AND tenant_id = %s"
        return self.execute_query(query, (user_id, tenant_id))

    def match_jobs(self, resume_id: int, top_k: int = 3) -> List[Dict]:
        """Match resume with available jobs"""
        # Get resume
        resume = self.get_by_id(resume_id)
        if not resume:
            return []

        # Get all jobs
        jobs = DatabaseOperations('jobs').get_all()
        
        matches = []
        for job in jobs:
            # Parse the stored vector
            import json
            resume_vector = json.loads(resume['vector_embedding'])
            job_vector = embed_text(job['description'])
            
            # Calculate similarity score
            similarity = calculate_similarity(
                resume_vector,
                job_vector
            )
            
            # Calculate skill overlap
            resume_skills = set(resume['skills'])
            job_skills = set(job['required_skills'])
            skill_overlap = len(resume_skills.intersection(job_skills))
            skill_overlap_score = skill_overlap / len(job_skills) if job_skills else 0
            
            # Store match in database
            match_data = {
                'tenant_id': resume.get('tenant_id'),
                'job_id': job['id'],
                'resume_id': resume_id,
                'match_score': similarity,
                'skills_matched': list(resume_skills.intersection(job_skills))
            }
            DatabaseOperations('job_matches').create(match_data)
            
            matches.append({
                'job': job,
                'match_score': similarity,
                'skill_overlap_score': skill_overlap_score,
                'matching_skills': list(resume_skills.intersection(job_skills)),
                'missing_skills': list(job_skills - resume_skills)
            })
        
        # Sort matches by score, with newest jobs first when scores tie.
        matches.sort(key=lambda x: (x['match_score'], x['job']['id']), reverse=True)
        return matches[:top_k]

resume_service = ResumeService()