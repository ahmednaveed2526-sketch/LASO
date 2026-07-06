"""
Comprehensive Unit Tests for Location Module
Member 3: Location & Search Module Developer
LASO App - Group 10
"""

import unittest
import math
from location_service import LocationService
from search_engine import SearchEngine, SearchFilter, SearchResult
from geo_utils import GeoUtils, BoundingBox
from config import Config


class TestGeoUtils(unittest.TestCase):
    """Test geographic utility functions"""
    
    def test_haversine_distance(self):
        """Test Haversine distance calculation"""
        # NYC to London (approximately)
        distance = GeoUtils.haversine_distance(40.7128, -74.0060, 51.5074, -0.1278)
        self.assertAlmostEqual(distance, 5570, delta=100)
        
        # Same point
        distance = GeoUtils.haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertEqual(distance, 0.0)
    
    def test_vincenty_distance(self):
        """Test Vincenty distance calculation"""
        distance = GeoUtils.vincenty_distance(40.7128, -74.0060, 51.5074, -0.1278)
        self.assertAlmostEqual(distance, 5570, delta=100)
        
        # Same point
        distance = GeoUtils.vincenty_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertEqual(distance, 0.0)
    
    def test_get_bounding_box(self):
        """Test bounding box calculation"""
        box = GeoUtils.get_bounding_box(40.7128, -74.0060, 10.0)
        
        self.assertIsInstance(box, BoundingBox)
        self.assertLess(box.min_lat, box.max_lat)
        self.assertLess(box.min_lon, box.max_lon)
        
        # Center should be approximately the input point
        center_lat, center_lon = box.center
        self.assertAlmostEqual(center_lat, 40.7128, delta=0.1)
        self.assertAlmostEqual(center_lon, -74.0060, delta=0.1)
    
    def test_is_point_in_box(self):
        """Test point in box check"""
        box = BoundingBox(40.0, -75.0, 41.0, -74.0)
        
        # Point inside
        self.assertTrue(GeoUtils.is_point_in_box(40.5, -74.5, box))
        
        # Point outside
        self.assertFalse(GeoUtils.is_point_in_box(42.0, -74.5, box))
        self.assertFalse(GeoUtils.is_point_in_box(40.5, -73.0, box))
    
    def test_validate_coordinates(self):
        """Test coordinate validation"""
        self.assertTrue(GeoUtils.validate_coordinates(40.7128, -74.0060))
        self.assertFalse(GeoUtils.validate_coordinates(100, -74.0060))
        self.assertFalse(GeoUtils.validate_coordinates(40.7128, -200))
        self.assertFalse(GeoUtils.validate_coordinates("invalid", -74.0060))
    
    def test_normalize_coordinates(self):
        """Test coordinate normalization"""
        lat, lon = GeoUtils.normalize_coordinates(100, -74.0060)
        self.assertEqual(lat, 90)
        
        lat, lon = GeoUtils.normalize_coordinates(40.7128, 200)
        self.assertAlmostEqual(lon, -160)
    
    def test_format_coordinates(self):
        """Test coordinate formatting"""
        formatted = GeoUtils.format_coordinates(40.7128, -74.0060)
        self.assertIn("40.712800", formatted)
        
        formatted_dms = GeoUtils.format_coordinates(40.7128, -74.0060, "dms")
        self.assertIn("°", formatted_dms)
    
    def test_parse_coordinates(self):
        """Test coordinate parsing"""
        # Decimal format
        coords = GeoUtils.parse_coordinates("40.7128, -74.0060")
        self.assertIsNotNone(coords)
        if coords:
            self.assertAlmostEqual(coords[0], 40.7128)
            self.assertAlmostEqual(coords[1], -74.0060)
        
        # DMS format
        coords = GeoUtils.parse_coordinates("40°42'46.1\"N, 74°00'21.6\"W")
        self.assertIsNotNone(coords)
        if coords:
            self.assertAlmostEqual(coords[0], 40.7128, delta=0.01)
            self.assertAlmostEqual(coords[1], -74.0060, delta=0.01)


class TestSearchEngine(unittest.TestCase):
    """Test search engine functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.search_engine = SearchEngine()
        self.providers = [
            {
                "id": 1,
                "name": "Pro Plumbing",
                "category": "plumber",
                "description": "Professional plumbing services",
                "rating": 4.8,
                "years_experience": 15,
                "price_range": "$$",
                "available": True
            },
            {
                "id": 2,
                "name": "Elite Electric",
                "category": "electrician",
                "description": "Premium electrical services",
                "rating": 4.9,
                "years_experience": 20,
                "price_range": "$$$",
                "available": True
            }
        ]
    
    def test_search_without_query(self):
        """Test search with empty query"""
        results = self.search_engine.search("", self.providers)
        self.assertEqual(len(results), 2)
    
    def test_search_with_query(self):
        """Test search with query"""
        results = self.search_engine.search("plumbing", self.providers)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider['name'], "Pro Plumbing")
    
    def test_search_with_filters(self):
        """Test search with filters"""
        filters = SearchFilter(
            category="electrician",
            min_rating=4.5,
            available_only=True
        )
        
        results = self.search_engine.search("electric", self.providers, filters=filters)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].provider['category'], "electrician")
    
    def test_relevance_scoring(self):
        """Test relevance scoring"""
        results = self.search_engine.search("plumbing", self.providers)
        self.assertGreater(len(results), 0)
        
        # Pro Plumbing should have higher relevance
        plumbing_result = next((r for r in results if r.provider['name'] == "Pro Plumbing"), None)
        self.assertIsNotNone(plumbing_result)
        self.assertGreater(plumbing_result.relevance_score, 0)
    
    def test_filter_by_rating(self):
        """Test rating filter"""
        filters = SearchFilter(min_rating=4.8)
        results = self.search_engine.search("", self.providers, filters=filters)
        self.assertEqual(len(results), 2)  # Both have rating >= 4.8
    
    def test_sort_by_distance(self):
        """Test sorting by distance"""
        # This would need location data, but we can test the sorting logic
        filters = SearchFilter(sort_by="distance")
        results = self.search_engine.search("", self.providers, filters=filters)
        self.assertEqual(len(results), 2)
    
    def test_get_search_suggestions(self):
        """Test search suggestions"""
        suggestions = self.search_engine.get_search_suggestions("plumb", self.providers)
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any("plumbing" in s.lower() for s in suggestions))
    
    def test_filter_counts(self):
        """Test filter counts"""
        counts = self.search_engine.get_filter_counts(self.providers)
        self.assertEqual(counts['total'], 2)
        self.assertEqual(counts['categories']['plumber'], 1)
        self.assertEqual(counts['categories']['electrician'], 1)


class TestLocationService(unittest.TestCase):
    """Test main location service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.service = LocationService(use_miles=False)
        self.providers = self.service.get_mock_providers()
    
    def test_initialization(self):
        """Test service initialization"""
        self.assertEqual(self.service.radius_unit, "km")
        self.assertIsNotNone(self.service.search_engine)
        self.assertGreater(len(self.providers), 0)
    
    def test_calculate_distance(self):
        """Test distance calculation"""
        distance = self.service.calculate_distance(40.7128, -74.0060, 40.7589, -73.9851)
        self.assertGreater(distance, 0)
        self.assertLess(distance, 10)  # Should be within NYC
    
    def test_get_current_location(self):
        """Test getting current location"""
        location = self.service.get_current_location()
        self.assertIsNotNone(location)
        self.assertEqual(len(location), 2)
    
    def test_get_nearby_providers(self):
        """Test nearby provider search"""
        nearby = self.service.get_nearby_providers(
            self.providers,
            40.7128, -74.0060,
            radius=5.0
        )
        self.assertGreater(len(nearby), 0)
        
        # Check that all providers have distance
        for provider in nearby:
            self.assertIn('distance', provider)
            self.assertLessEqual(provider['distance'], 5.0)
    
    def test_get_nearby_providers_with_category(self):
        """Test nearby search with category filter"""
        nearby = self.service.get_nearby_providers(
            self.providers,
            40.7128, -74.0060,
            radius=10.0,
            category="plumber"
        )
        
        for provider in nearby:
            self.assertEqual(provider['category'].lower(), "plumber")
    
    def test_geocode_address(self):
        """Test address geocoding"""
        coords = self.service.geocode_address("New York")
        self.assertIsNotNone(coords)
        
        if coords:
            self.assertAlmostEqual(coords[0], 40.7128, delta=0.1)
            self.assertAlmostEqual(coords[1], -74.0060, delta=0.1)
    
    def test_reverse_geocode(self):
        """Test reverse geocoding"""
        address = self.service.reverse_geocode(40.7128, -74.0060)
        self.assertIsNotNone(address)
        self.assertIn("New York", address)
    
    def test_search_providers(self):
        """Test provider search"""
        results = self.service.search_providers("plumbing", 40.7128, -74.0060)
        self.assertGreater(len(results), 0)
        
        # Check that results have relevance scores
        for result in results:
            self.assertIn('relevance_score', result)
    
    def test_get_provider_categories(self):
        """Test getting provider categories"""
        categories = self.service.get_provider_categories()
        self.assertGreater(len(categories), 0)
        self.assertIn("Plumber", categories)
        self.assertIn("Electrician", categories)
    
    def test_get_nearby_categories(self):
        """Test nearby category counts"""
        counts = self.service.get_nearby_categories(40.7128, -74.0060, radius=10.0)
        self.assertGreater(len(counts), 0)
        self.assertIn("Plumber", counts)
    
    def test_get_location_info(self):
        """Test location info"""
        info = self.service.get_location_info(40.7128, -74.0060)
        self.assertIn('coordinates', info)
        self.assertIn('address', info)
        self.assertIn('nearby_providers_count', info)
        self.assertIn('categories', info)
    
    def test_update_provider_location(self):
        """Test provider location update"""
        result = self.service.update_provider_location(1, 40.7128, -74.0060)
        self.assertTrue(result)
        
        # Verify update
        providers = self.service.get_mock_providers()
        updated = next((p for p in providers if p.get('id') == 1), None)
        self.assertIsNotNone(updated)
        self.assertEqual(updated['latitude'], 40.7128)
    
    def test_add_remove_provider(self):
        """Test adding and removing providers"""
        new_provider = {
            "name": "Test Provider",
            "category": "test",
            "latitude": 40.7128,
            "longitude": -74.0060
        }
        
        # Add
        self.service.add_provider(new_provider)
        providers = self.service.get_mock_providers()
        self.assertTrue(any(p.get('name') == "Test Provider" for p in providers))
        
        # Remove
        provider_id = next(p.get('id') for p in providers if p.get('name') == "Test Provider")
        result = self.service.remove_provider(provider_id)
        self.assertTrue(result)
        
        providers = self.service.get_mock_providers()
        self.assertFalse(any(p.get('id') == provider_id for p in providers))
    
    def test_get_statistics(self):
        """Test statistics"""
        stats = self.service.get_statistics()
        self.assertIn('total_providers', stats)
        self.assertIn('categories', stats)
        self.assertIn('radius_unit', stats)
        self.assertEqual(stats['total_providers'], len(self.providers))


class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def test_end_to_end_search_flow(self):
        """Test complete search flow"""
        # Setup
        service = LocationService()
        providers = service.get_mock_providers()
        
        # 1. Get user location
        user_location = service.get_current_location()
        self.assertIsNotNone(user_location)
        user_lat, user_lon = user_location
        
        # 2. Search for nearby providers
        nearby = service.get_nearby_providers(
            providers, user_lat, user_lon, radius=10.0
        )
        self.assertGreater(len(nearby), 0)
        
        # 3. Filter by category
        plumbers = service.get_nearby_providers(
            providers, user_lat, user_lon, radius=10.0, category="plumber"
        )
        self.assertGreater(len(plumbers), 0)
        
        # 4. Search with query
        search_results = service.search_providers("plumbing", user_lat, user_lon)
        self.assertGreater(len(search_results), 0)
        
        # 5. Get provider details
        if search_results:
            provider = search_results[0]
            self.assertIn('name', provider)
            self.assertIn('distance', provider)
    
    def test_geocoding_flow(self):
        """Test geocoding flow"""
        service = LocationService()
        
        # 1. Geocode address
        coords = service.geocode_address("New York")
        self.assertIsNotNone(coords)
        
        if coords:
            lat, lon = coords
            
            # 2. Reverse geocode
            address = service.reverse_geocode(lat, lon)
            self.assertIsNotNone(address)
            
            # 3. Get location info
            info = service.get_location_info(lat, lon)
            self.assertIn('nearby_providers_count', info)


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)