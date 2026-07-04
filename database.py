# database.py
import json
from datetime import datetime
from typing import List, Optional, Dict
from models import Rating, Review, ProviderRating, ServiceCategory

class Database:
    def __init__(self, data_file: str = 'data.json'):
        self.data_file = data_file
        self.ratings: List[Rating] = []
        self.reviews: List[Review] = []
        self.provider_ratings: Dict[int, ProviderRating] = {}
        self._load_data()
    
    def _load_data(self):
        """Load data from JSON file"""
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                # Load ratings
                for rating_data in data.get('ratings', []):
                    rating = Rating(
                        rating_id=rating_data['rating_id'],
                        service_id=rating_data['service_id'],
                        customer_id=rating_data['customer_id'],
                        provider_id=rating_data['provider_id'],
                        rating=rating_data['rating'],
                        comment=rating_data.get('comment', ''),
                        timestamp=datetime.fromisoformat(rating_data['timestamp']),
                        category=ServiceCategory(rating_data['category'])
                    )
                    self.ratings.append(rating)
                
                # Load reviews
                for review_data in data.get('reviews', []):
                    review = Review(
                        review_id=review_data['review_id'],
                        rating_id=review_data['rating_id'],
                        reviewer_id=review_data['reviewer_id'],
                        review_text=review_data['review_text'],
                        helpful_count=review_data.get('helpful_count', 0),
                        timestamp=datetime.fromisoformat(review_data['timestamp']),
                        is_verified=review_data.get('is_verified', False)
                    )
                    self.reviews.append(review)
        except FileNotFoundError:
            # Initialize empty data
            pass
    
    def save_data(self):
        """Save data to JSON file"""
        data = {
            'ratings': [r.to_dict() for r in self.ratings],
            'reviews': [r.to_dict() for r in self.reviews]
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_rating(self, rating: Rating):
        """Add a new rating"""
        self.ratings.append(rating)
        self.save_data()
    
    def add_review(self, review: Review):
        """Add a new review"""
        self.reviews.append(review)
        self.save_data()
    
    def get_provider_ratings(self, provider_id: int) -> ProviderRating:
        """Get all ratings for a provider"""
        provider_rating = ProviderRating(provider_id)
        provider_rating.ratings = [
            r for r in self.ratings if r.provider_id == provider_id
        ]
        provider_rating.calculate_average()
        return provider_rating
    
    def get_ratings_by_category(self, category: ServiceCategory) -> List[Rating]:
        """Get ratings for a specific service category"""
        return [r for r in self.ratings if r.category == category]
    
    def get_ratings_by_customer(self, customer_id: int) -> List[Rating]:
        """Get ratings given by a specific customer"""
        return [r for r in self.ratings if r.customer_id == customer_id]
    
    def get_ratings_by_service(self, service_id: int) -> List[Rating]:
        """Get ratings for a specific service"""
        return [r for r in self.ratings if r.service_id == service_id]