"""
User service for handling user-related operations
"""
from typing import Dict, List, Optional
from werkzeug.security import generate_password_hash, check_password_hash
from db.database import DatabaseOperations

class UserService(DatabaseOperations):
    def __init__(self):
        super().__init__('users')

    def create_user(self, data: Dict) -> Dict:
        """Create a new user"""
        # Hash the password
        data['password_hash'] = generate_password_hash(data.pop('password'))
        
        # Insert into database
        user_id = self.create(data)
        user = self.get_by_id(user_id)
        if user:
            del user['password_hash']  # Don't return the password hash
        return user

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user"""
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (username,))
        
        if result and check_password_hash(result[0]['password_hash'], password):
            user = result[0]
            del user['password_hash']  # Don't return the password hash
            return user
        return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        query = "SELECT * FROM users WHERE username = %s"
        result = self.execute_query(query, (username,))
        if result:
            user = result[0]
            del user['password_hash']  # Don't return the password hash
            return user
        return None

user_service = UserService()
