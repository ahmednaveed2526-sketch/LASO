# utils.py
from datetime import datetime
from typing import List, Dict, Optional
import json
import re

class Utils:
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number"""
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def format_rating(rating: float) -> str:
        """Format rating for display"""
        return f"{rating:.1f} ★"
    
    @staticmethod
    def calculate_stars(rating: float) -> str:
        """Convert rating to star string"""
        full_stars = int(rating)
        half_star = 1 if rating - full_stars >= 0.5 else 0
        empty_stars = 5 - full_stars - half_star
        
        return "★" * full_stars + "½" * half_star + "☆" * empty_stars
    
    @staticmethod
    def get_rating_description(rating: float) -> str:
        """Get description for rating"""
        descriptions = {
            5.0: "Excellent",
            4.5: "Very Good",
            4.0: "Good",
            3.5: "Above Average",
            3.0: "Average",
            2.5: "Below Average",
            2.0: "Poor",
            1.5: "Very Poor",
            1.0: "Terrible"
        }
        
        # Find closest rating
        closest = min(descriptions.keys(), key=lambda x: abs(x - rating))
        return descriptions[closest]
    
    @staticmethod
    def filter_ratings(ratings: List, min_rating: float = None, 
                      max_rating: float = None, 
                      category: str = None) -> List:
        """Filter ratings by criteria"""
        filtered = ratings
        
        if min_rating is not None:
            filtered = [r for r in filtered if r.rating >= min_rating]
        
        if max_rating is not None:
            filtered = [r for r in filtered if r.rating <= max_rating]
        
        if category is not None:
            filtered = [r for r in filtered if r.category.value == category]
        
        return filtered
    
    @staticmethod
    def sort_ratings(ratings: List, sort_by: str = 'timestamp', 
                    reverse: bool = True) -> List:
        """Sort ratings by criteria"""
        valid_sort_keys = ['timestamp', 'rating', 'rating_id']
        
        if sort_by not in valid_sort_keys:
            sort_by = 'timestamp'
        
        return sorted(ratings, key=lambda x: getattr(x, sort_by), reverse=reverse)
    
    @staticmethod
    def generate_summary(stats: Dict) -> str:
        """Generate human-readable summary from stats"""
        summary = []
        summary.append(f"Provider ID: {stats.get('provider_id', 'N/A')}")
        summary.append(f"Average Rating: {stats.get('average_rating', 0):.1f} ★")
        summary.append(f"Total Ratings: {stats.get('total_ratings', 0)}")
        
        distribution = stats.get('rating_distribution', {})
        if distribution:
            summary.append("\nRating Distribution:")
            for rating, count in sorted(distribution.items()):
                bar = "█" * count
                summary.append(f"  {rating:.1f}★: {bar} ({count})")
        
        latest = stats.get('latest_ratings', [])
        if latest:
            summary.append("\nLatest Ratings:")
            for r in latest[:3]:
                summary.append(f"  Rating: {r.rating:.1f}★ - {r.comment[:30]}...")
        
        return "\n".join(summary)
    
    @staticmethod
    def save_to_json(data: Dict, filename: str):
        """Save data to JSON file"""
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    @staticmethod
    def load_from_json(filename: str) -> Dict:
        """Load data from JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}