from typing import List, Dict, Any
import numpy as np
from .nlp_service import NLPService
from .learning_service import LearningService
from sklearn.metrics.pairwise import cosine_similarity

class AIFeedbackService:
    """
    Provides AI-powered feedback and recommendations for:
    - Performance reviews
    - Learning paths
    - Career development
    - Skill gaps
    """
    def __init__(self):
        self.nlp_service = NLPService()
        self.learning_service = LearningService()
        
    def analyze_performance_review(self, review_text: str) -> Dict[str, Any]:
        """
        Analyze performance review text to extract:
        - Key achievements
        - Areas for improvement
        - Sentiment
        - Skill mentions
        """
        # Get sentiment
        sentiment = self.nlp_service.analyze_sentiment(review_text)
        
        # Extract entities (skills, projects, etc.)
        entities = self.nlp_service.extract_entities(review_text)
        
        # Get text embedding for similarity comparison
        embedding = self.nlp_service.get_embedding(review_text)
        
        return {
            'sentiment': sentiment,
            'entities': entities,
            'embedding': embedding.tolist()
        }
        
    def recommend_learning_path(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Recommend personalized learning paths based on:
        - Current skills
        - Career goals
        - Performance reviews
        - Industry trends
        """
        # Get user's current skills
        current_skills = user_profile.get('skills', [])
        
        # Get career goals
        career_goals = user_profile.get('career_goals', [])
        
        # Get all available learning paths
        all_paths = self.learning_service.get_all_paths()
        
        # Calculate similarity scores
        scores = []
        user_embedding = self.nlp_service.get_embedding(
            ' '.join(current_skills + career_goals)
        )
        
        for path in all_paths:
            path_embedding = self.nlp_service.get_embedding(
                f"{path['title']} {path['description']} {' '.join(path['skills'])}"
            )
            similarity = cosine_similarity(
                user_embedding.reshape(1, -1),
                path_embedding.reshape(1, -1)
            )[0][0]
            scores.append((path, similarity))
            
        # Sort by similarity score
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top recommendations
        return [
            {**path, 'relevance_score': score}
            for path, score in scores[:5]
        ]
        
    def identify_skill_gaps(
        self, 
        current_skills: List[str],
        target_role: str
    ) -> Dict[str, Any]:
        """
        Identify skill gaps between current skills and target role
        """
        # Get required skills for target role
        role_skills = self.learning_service.get_role_skills(target_role)
        
        # Convert to embeddings
        current_embeddings = np.array([
            self.nlp_service.get_embedding(skill)
            for skill in current_skills
        ])
        
        role_embeddings = np.array([
            self.nlp_service.get_embedding(skill)
            for skill in role_skills
        ])
        
        # Calculate similarities
        similarities = cosine_similarity(current_embeddings, role_embeddings)
        
        # Identify gaps (skills with no close match)
        gaps = []
        for i, skill in enumerate(role_skills):
            if not any(similarities[:, i] > 0.8):  # Threshold for similarity
                gaps.append({
                    'skill': skill,
                    'importance': 'High',
                    'closest_match': current_skills[
                        similarities[:, i].argmax()
                    ] if len(current_skills) > 0 else None,
                    'similarity_score': similarities[:, i].max()
                })
                
        return {
            'gaps': gaps,
            'total_gaps': len(gaps),
            'current_skills_count': len(current_skills),
            'required_skills_count': len(role_skills)
        }
        
    def generate_development_plan(
        self,
        user_profile: Dict[str, Any],
        skill_gaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate a personalized development plan
        """
        # Get recommended courses for each skill gap
        recommendations = []
        for gap in skill_gaps:
            courses = self.learning_service.find_courses(gap['skill'])
            recommendations.extend(courses)
            
        # Prioritize recommendations
        recommendations.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return {
            'short_term_goals': recommendations[:3],
            'medium_term_goals': recommendations[3:6],
            'long_term_goals': recommendations[6:9],
            'estimated_completion_time': f"{len(skill_gaps) * 3} months",
            'priority_skills': [gap['skill'] for gap in skill_gaps if gap.get('importance') == 'High']
        }
