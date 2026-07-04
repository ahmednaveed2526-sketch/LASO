# models.py
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

class ServiceCategory(Enum):
    PLUMBING = "Plumbing"
    ELECTRICAL = "Electrical"
    CARPENTRY = "Carpentry"
    CLEANING = "Cleaning"
    PAINTING = "Painting"
    HVAC = "HVAC"
    PEST_CONTROL = "Pest Control"
    OTHER = "Other"

class Rating:
    def __init__(self, rating_id: int, service_id: int, customer_id: int, 
                 provider_id: int, rating: float, comment: str, 
                 timestamp: datetime, category: ServiceCategory):
        self.rating_id = rating_id
        self.service_id = service_id
        self.customer_id = customer_id
        self.provider_id = provider_id
        self.rating = rating
        self.comment = comment
        self.timestamp = timestamp
        self.category = category
    
    def to_dict(self) -> Dict:
        return {
            'rating_id': self.rating_id,
            'service_id': self.service_id,
            'customer_id': self.customer_id,
            'provider_id': self.provider_id,
            'rating': self.rating,
            'comment': self.comment,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'category': self.category.value
        }

class Review:
    def __init__(self, review_id: int, rating_id: int, reviewer_id: int,
                 review_text: str, helpful_count: int, timestamp: datetime,
                 is_verified: bool = False):
        self.review_id = review_id
        self.rating_id = rating_id
        self.reviewer_id = reviewer_id
        self.review_text = review_text
        self.helpful_count = helpful_count
        self.timestamp = timestamp
        self.is_verified = is_verified
    
    def to_dict(self) -> Dict:
        return {
            'review_id': self.review_id,
            'rating_id': self.rating_id,
            'reviewer_id': self.reviewer_id,
            'review_text': self.review_text,
            'helpful_count': self.helpful_count,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_verified': self.is_verified
        }

class ProviderRating:
    def __init__(self, provider_id: int):
        self.provider_id = provider_id
        self.ratings: List[Rating] = []
        self.average_rating = 0.0
        self.total_ratings = 0
    
    def calculate_average(self) -> float:
        if not self.ratings:
            return 0.0
        total = sum(r.rating for r in self.ratings)
        self.average_rating = total / len(self.ratings)
        return self.average_rating
    
    def add_rating(self, rating: Rating):
        self.ratings.append(rating)
        self.total_ratings = len(self.ratings)
        self.calculate_average()