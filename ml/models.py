from sklearn.base import BaseEstimator, TransformerMixin
from typing import List, Dict, Any
import numpy as np
import pandas as pd
from datetime import datetime

class EmployeeDataPreprocessor(BaseEstimator, TransformerMixin):
    """
    Preprocessor for employee data that handles:
    - Missing values
    - Feature engineering
    - Categorical encoding
    - Numerical scaling
    """
    def __init__(self):
        self.categorical_features = ['department', 'role', 'education']
        self.numerical_features = ['years_experience', 'performance_score', 'training_hours']
        
    def fit(self, X: pd.DataFrame, y=None):
        return self
        
    def transform(self, X: pd.DataFrame) -> np.ndarray:
        X_processed = X.copy()
        
        # Handle missing values
        for feature in self.numerical_features:
            X_processed[feature].fillna(X_processed[feature].median(), inplace=True)
            
        for feature in self.categorical_features:
            X_processed[feature].fillna(X_processed[feature].mode()[0], inplace=True)
            
        # Feature engineering
        X_processed['days_since_last_promotion'] = (
            datetime.now() - pd.to_datetime(X_processed['last_promotion_date'])
        ).dt.days
        
        # One-hot encoding for categorical features
        X_processed = pd.get_dummies(
            X_processed, 
            columns=self.categorical_features,
            drop_first=True
        )
        
        return X_processed.values

class PerformancePredictor:
    """
    Predicts employee performance based on historical data
    Uses ensemble of models for better accuracy
    """
    def __init__(self, models: List[BaseEstimator]):
        self.models = models
        self.preprocessor = EmployeeDataPreprocessor()
        
    def train(self, X: pd.DataFrame, y: np.ndarray):
        """Train all models in the ensemble"""
        X_processed = self.preprocessor.fit_transform(X)
        
        for model in self.models:
            model.fit(X_processed, y)
            
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Get ensemble predictions"""
        X_processed = self.preprocessor.transform(X)
        predictions = []
        
        for model in self.models:
            pred = model.predict(X_processed)
            predictions.append(pred)
            
        # Average predictions from .all models
        return np.mean(predictions, axis=0)
        
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance scores"""
        feature_importance = {}
        # Implementation depends on the specific models used
        return feature_importance
