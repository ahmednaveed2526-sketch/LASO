# test_cases.py
import unittest
from datetime import datetime
from rating_system import RatingSystem
from models import ServiceCategory, Rating, Review, ProviderRating
from database import Database

class TestRatingSystem(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.rating_system = RatingSystem()
        self.db = Database('test_data.json')
        # Clear any existing test data
        self.db.ratings.clear()
        self.db.reviews.clear()
        self.rating_system.db = self.db
    
    def tearDown(self):
        """Clean up after tests"""
        self.db.ratings.clear()
        self.db.reviews.clear()
        self.db.save_data()
    
    def test_submit_rating_valid(self):
        """Test submitting a valid rating"""
        result = self.rating_system.submit_rating(
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=4.5,
            comment="Great service!",
            category=ServiceCategory.PLUMBING
        )
        self.assertTrue(result)
        self.assertEqual(len(self.db.ratings), 1)
        self.assertEqual(self.db.ratings[0].rating, 4.5)
    
    def test_submit_rating_invalid_value(self):
        """Test submitting an invalid rating value"""
        result = self.rating_system.submit_rating(
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=6.0,  # Invalid rating
            comment="Great service!",
            category=ServiceCategory.PLUMBING
        )
        self.assertFalse(result)
        self.assertEqual(len(self.db.ratings), 0)
    
    def test_submit_rating_invalid_category(self):
        """Test submitting with invalid category"""
        result = self.rating_system.submit_rating(
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=4.5,
            comment="Great service!",
            category="INVALID_CATEGORY"  # Invalid category
        )
        self.assertFalse(result)
    
    def test_submit_review_valid(self):
        """Test submitting a valid review"""
        # First submit a rating
        self.rating_system.submit_rating(
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=4.5,
            comment="Great service!",
            category=ServiceCategory.PLUMBING
        )
        
        # Submit a review
        result = self.rating_system.submit_review(
            rating_id=1,
            reviewer_id=301,
            review_text="Very professional work!"
        )
        self.assertTrue(result)
        self.assertEqual(len(self.db.reviews), 1)
    
    def test_submit_review_invalid_rating(self):
        """Test submitting a review for non-existent rating"""
        result = self.rating_system.submit_review(
            rating_id=999,  # Non-existent rating
            reviewer_id=301,
            review_text="Very professional work!"
        )
        self.assertFalse(result)
    
    def test_get_provider_stats(self):
        """Test getting provider statistics"""
        # Submit multiple ratings for the same provider
        for i in range(5):
            self.rating_system.submit_rating(
                service_id=i+1,
                customer_id=100+i,
                provider_id=201,
                rating=3.0 + i * 0.5,
                comment=f"Service {i+1}",
                category=ServiceCategory.PLUMBING
            )
        
        stats = self.rating_system.get_provider_stats(201)
        self.assertEqual(stats['total_ratings'], 5)
        self.assertAlmostEqual(stats['average_rating'], 4.0, places=1)
    
    def test_get_category_average(self):
        """Test getting average rating by category"""
        # Submit ratings for different categories
        categories = [ServiceCategory.PLUMBING, ServiceCategory.ELECTRICAL]
        for i, category in enumerate(categories):
            self.rating_system.submit_rating(
                service_id=i+1,
                customer_id=100+i,
                provider_id=200+i,
                rating=4.0 + i,
                comment=f"Category {category.value}",
                category=category
            )
        
        avg_plumbing = self.rating_system.get_category_average(ServiceCategory.PLUMBING)
        avg_electrical = self.rating_system.get_category_average(ServiceCategory.ELECTRICAL)
        
        self.assertEqual(avg_plumbing, 4.0)
        self.assertEqual(avg_electrical, 5.0)
    
    def test_mark_review_helpful(self):
        """Test marking a review as helpful"""
        # Submit rating and review
        self.rating_system.submit_rating(
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=4.5,
            comment="Great service!",
            category=ServiceCategory.PLUMBING
        )
        self.rating_system.submit_review(
            rating_id=1,
            reviewer_id=301,
            review_text="Very professional work!"
        )
        
        # Mark as helpful
        result = self.rating_system.mark_review_helpful(1)
        self.assertTrue(result)
        
        # Verify helpful count
        review = self.db.reviews[0]
        self.assertEqual(review.helpful_count, 1)
    
    def test_get_customer_ratings(self):
        """Test getting ratings by customer"""
        # Submit ratings for different customers
        for i in range(3):
            self.rating_system.submit_rating(
                service_id=i+1,
                customer_id=101,
                provider_id=201+i,
                rating=4.0 + i * 0.5,
                comment=f"Service {i+1}",
                category=ServiceCategory.PLUMBING
            )
        
        customer_ratings = self.rating_system.get_customer_ratings(101)
        self.assertEqual(len(customer_ratings), 3)
        self.assertEqual(customer_ratings[0].rating, 4.0)
    
    def test_rating_average_calculation(self):
        """Test average rating calculation"""
        provider_rating = ProviderRating(201)
        
        # Add ratings
        for i in range(3):
            rating = Rating(
                rating_id=i+1,
                service_id=i+1,
                customer_id=100+i,
                provider_id=201,
                rating=3.0 + i,
                comment=f"Test {i+1}",
                timestamp=datetime.now(),
                category=ServiceCategory.PLUMBING
            )
            provider_rating.add_rating(rating)
        
        self.assertEqual(provider_rating.total_ratings, 3)
        self.assertAlmostEqual(provider_rating.average_rating, 4.0, places=1)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = Database('test_data.json')
        self.db.ratings.clear()
        self.db.reviews.clear()
    
    def tearDown(self):
        self.db.ratings.clear()
        self.db.reviews.clear()
        self.db.save_data()
    
    def test_add_and_retrieve_rating(self):
        """Test adding and retrieving a rating"""
        rating = Rating(
            rating_id=1,
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=4.5,
            comment="Excellent!",
            timestamp=datetime.now(),
            category=ServiceCategory.PLUMBING
        )
        self.db.add_rating(rating)
        
        provider_rating = self.db.get_provider_ratings(201)
        self.assertEqual(len(provider_rating.ratings), 1)
        self.assertEqual(provider_rating.ratings[0].rating, 4.5)
    
    def test_save_and_load_data(self):
        """Test saving and loading data"""
        rating = Rating(
            rating_id=1,
            service_id=1,
            customer_id=101,
            provider_id=201,
            rating=4.5,
            comment="Excellent!",
            timestamp=datetime.now(),
            category=ServiceCategory.PLUMBING
        )
        self.db.add_rating(rating)
        
        # Create new database instance to test loading
        new_db = Database('test_data.json')
        provider_rating = new_db.get_provider_ratings(201)
        self.assertEqual(len(provider_rating.ratings), 1)

if __name__ == '__main__':
    unittest.main()