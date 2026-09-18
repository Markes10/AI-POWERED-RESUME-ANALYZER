"""
Recommender utilities for Learning Path Recommender.

- Hybrid recommendations using LightFM
- Fallback to stub recommendations if no model is trained
"""

import os
from typing import List, Dict, Any
import numpy as np

try:
    from lightfm import LightFM
    from lightfm.data import Dataset
    _lightfm_available = True
except ImportError:
    _lightfm_available = False


# -------------------------------
# Recommender Service
# -------------------------------
class RecommenderService:
    def __init__(self):
        self.model = None
        self.dataset = None
        self.user_mapping = {}
        self.item_mapping = {}

    def train(
        self,
        interactions: List[tuple],
        users: List[str],
        items: List[str],
        epochs: int = 20
    ) -> Dict[str, Any]:
        """
        Train a LightFM hybrid model.

        interactions: list of (user_id, item_id)
        users: list of all user IDs
        items: list of all item IDs
        """
        if not _lightfm_available:
            raise ImportError("LightFM not installed. Run `pip install lightfm`.")

        dataset = Dataset()
        dataset.fit(users, items)

        (interactions_matrix, _) = dataset.build_interactions(interactions)

        model = LightFM(loss="warp")
        model.fit(interactions_matrix, epochs=epochs, num_threads=4)

        # Save state
        self.model = model
        self.dataset = dataset

        # Store mappings
        self.user_mapping, self.item_mapping, _ = dataset.mapping()

        return {"status": "trained", "epochs": epochs, "users": len(users), "items": len(items)}

    def recommend(self, user_id: str, top_k: int = 5) -> List[str]:
        """
        Recommend items (courses) for a user.
        """
        if not self.model or not self.dataset:
            # Stub fallback
            fallback_courses = [
                "Python for Data Science",
                "Effective Communication",
                "Leadership 101",
                "Advanced SQL",
                "Project Management Essentials",
            ]
            return fallback_courses[:top_k]

        if user_id not in self.user_mapping:
            return []

        n_items = len(self.item_mapping)
        user_index = self.user_mapping[user_id]

        scores = self.model.predict(user_index, np.arange(n_items))
        top_items = np.argsort(-scores)[:top_k]

        # Reverse mapping from .ID -> name
        id_to_item = {v: k for k, v in self.item_mapping.items()}
        return [id_to_item[i] for i in top_items]


# -------------------------------
# Singleton
# -------------------------------
_recommender_instance: RecommenderService = None


def get_recommender() -> RecommenderService:
    """
    Get a singleton recommender instance.
    """
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = RecommenderService()
    return _recommender_instance
    return StreamAnomalyDetector() # Replace with actual model