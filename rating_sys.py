# rating_system.py
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from models import Rating, Review, ProviderRating, ServiceCategory
from database import Database

class RatingSystem:
    def __init__(self):
        self.db = Database()
        self._next_rating_id = len(self.db.ratings) + 1
        self._next_review_id = len(self.db.reviews) + 1
    
    def submit_rating(self, service_id: int, customer_id: int, 
                     provider_id: int, rating: float, 
                     comment: str, category: ServiceCategory) -> bool:
        """
        Submit a rating for a service
        Returns: True if successful, False otherwise
        """
        # Validate rating value
        if not 1.0 <= rating <= 5.0:
            print("Rating must be between 1.0 and 5.0")
            return False
        
        # Validate category
        if not isinstance(category, ServiceCategory):
            print("Invalid service category")
            return False
        
        # Create rating object
        new_rating = Rating(
            rating_id=self._next_rating_id,
            service_id=service_id,
            customer_id=customer_id,
            provider_id=provider_id,
            rating=rating,
            comment=comment,
            timestamp=datetime.now(),
            category=category
        )
        
        # Save to database
        self.db.add_rating(new_rating)
        self._next_rating_id += 1
        print(f"Rating submitted successfully! Rating ID: {new_rating.rating_id}")
        return True
    
    def submit_review(self, rating_id: int, reviewer_id: int, 
                     review_text: str, is_verified: bool = False) -> bool:
        """
        Submit a review for a rating
        Returns: True if successful, False otherwise
        """
        # Check if rating exists
        rating_exists = any(r.rating_id == rating_id for r in self.db.ratings)
        if not rating_exists:
            print("Rating not found!")
            return False
        
        # Create review object
        new_review = Review(
            review_id=self._next_review_id,
            rating_id=rating_id,
            reviewer_id=reviewer_id,
            review_text=review_text,
            helpful_count=0,
            timestamp=datetime.now(),
            is_verified=is_verified
        )
        
        self.db.add_review(new_review)
        self._next_review_id += 1
        print(f"Review submitted successfully! Review ID: {new_review.review_id}")
        return True
    
    def get_provider_stats(self, provider_id: int) -> Dict:
        """
        Get statistics for a service provider
        Returns: Dictionary with provider stats
        """
        provider_rating = self.db.get_provider_ratings(provider_id)
        ratings = provider_rating.ratings
        
        if not ratings:
            return {
                'provider_id': provider_id,
                'average_rating': 0.0,
                'total_ratings': 0,
                'rating_distribution': {},
                'latest_ratings': []
            }
        
        # Calculate rating distribution
        distribution = {1.0: 0, 2.0: 0, 3.0: 0, 4.0: 0, 5.0: 0}
        for r in ratings:
            rounded = round(r.rating * 2) / 2  # Round to nearest 0.5
            distribution[rounded] = distribution.get(rounded, 0) + 1
        
        return {
            'provider_id': provider_id,
            'average_rating': provider_rating.average_rating,
            'total_ratings': len(ratings),
            'rating_distribution': distribution,
            'latest_ratings': sorted(ratings, key=lambda x: x.timestamp, reverse=True)[:5]
        }
    
    def get_category_average(self, category: ServiceCategory) -> float:
        """
        Get average rating for a specific category
        """
        category_ratings = self.db.get_ratings_by_category(category)
        if not category_ratings:
            return 0.0
        return sum(r.rating for r in category_ratings) / len(category_ratings)
    
    def get_customer_ratings(self, customer_id: int) -> List[Rating]:
        """
        Get all ratings submitted by a customer
        """
        return self.db.get_ratings_by_customer(customer_id)
    
    def get_service_ratings(self, service_id: int) -> List[Rating]:
        """
        Get all ratings for a specific service
        """
        return self.db.get_ratings_by_service(service_id)
    
    def mark_review_helpful(self, review_id: int) -> bool:
        """
        Mark a review as helpful
        Returns: True if successful, False otherwise
        """
        for review in self.db.reviews:
            if review.review_id == review_id:
                review.helpful_count += 1
                self.db.save_data()
                print(f"Review {review_id} marked as helpful!")
                return True
        print("Review not found!")
        return False