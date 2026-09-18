"""
Job service for handling job-related operations
"""
from typing import Dict, List, Optional
from db.database import DatabaseOperations

class JobService(DatabaseOperations):
    def __init__(self):
        super().__init__('jobs')

    def create_job(self, data: Dict) -> Dict:
        """Create a new job"""
        # Insert into database
        job_id = self.create(data)
        return self.get_by_id(job_id)

    def search_jobs(self, keywords: List[str]) -> List[Dict]:
        """Search jobs by keywords"""
        where_clauses = []
        params = []
        for keyword in keywords:
            where_clauses.append("(title LIKE %s OR description LIKE %s)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        where_clause = " OR ".join(where_clauses)
        query = f"SELECT * FROM jobs WHERE {where_clause}"
        return self.execute_query(query, tuple(params))

    def get_department_jobs(self, department: str) -> List[Dict]:
        """Get all jobs in a department"""
        query = "SELECT * FROM jobs WHERE department = %s"
        return self.execute_query(query, (department,))

job_service = JobService()
