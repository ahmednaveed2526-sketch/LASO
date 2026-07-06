"""
Unit Tests for Map Integration Module
Member 3: Location & Search Module Developer
LASO App - Group 10

This module provides comprehensive unit tests for the map integration features,
including HTML generation, marker clustering, heatmaps, and route visualization.
"""

import unittest
import os
import json
import tempfile
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

from map_integration import MapIntegration
from location_service import LocationService
from sample_data import SampleDataGenerator


class TestMapIntegration(unittest.TestCase):
    """Test suite for MapIntegration class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.location_service = LocationService()
        self.map_integration = MapIntegration(self.location_service)
        self.generator = SampleDataGenerator()
        
        # Generate test providers
        self.providers = self.generator.generate_providers(count=20)
        
        # Test coordinates
        self.test_lat = 40.7128
        self.test_lon = -74.0060
        
    def test_initialization(self):
        """Test MapIntegration initialization"""
        self.assertIsNotNone(self.map_integration)
        self.assertIsNotNone(self.map_integration.location_service)
        self.assertIsInstance(self.map_integration.category_colors, dict)
        self.assertIsInstance(self.map_integration.category_icons, dict)
        self.assertGreater(len(self.map_integration.category_colors), 0)
        
    def test_get_category_color(self):
        """Test category color retrieval"""
        # Test known category
        color = self.map_integration._get_category_color("Plumber")
        self.assertEqual(color, '#3498db')
        
        # Test unknown category (should return default)
        color = self.map_integration._get_category_color("UnknownCategory")
        self.assertEqual(color, '#78909c')
        
        # Test case insensitivity
        color = self.map_integration._get_category_color("plumber")
        self.assertEqual(color, '#3498db')
        
    def test_get_category_icon(self):
        """Test category icon retrieval"""
        # Test known category
        icon = self.map_integration._get_category_icon("Plumber")
        self.assertEqual(icon, '🔧')
        
        # Test unknown category (should return default)
        icon = self.map_integration._get_category_icon("UnknownCategory")
        self.assertEqual(icon, '📍')
        
        # Test case insensitivity
        icon = self.map_integration._get_category_icon("plumber")
        self.assertEqual(icon, '🔧')
        
    def test_format_distance(self):
        """Test distance formatting"""
        # Test kilometers
        formatted = self.map_integration._format_distance(5.5)
        self.assertEqual(formatted, "5.50 km")
        
        # Test meters (less than 1 km)
        formatted = self.map_integration._format_distance(0.5)
        self.assertEqual(formatted, "500 m")
        
        # Test very short distance
        formatted = self.map_integration._format_distance(0.05)
        self.assertEqual(formatted, "50 m")
        
        # Test None value
        formatted = self.map_integration._format_distance(None)
        self.assertEqual(formatted, "")
        
    def test_generate_html_map(self):
        """Test HTML map generation"""
        html = self.map_integration.generate_html_map(
            self.providers,
            center_lat=self.test_lat,
            center_lon=self.test_lon,
            zoom=13,
            title="Test Map",
            cluster=True,
            user_location=(self.test_lat, self.test_lon)
        )
        
        # Check that HTML was generated
        self.assertIsNotNone(html)
        self.assertIsInstance(html, str)
        self.assertGreater(len(html), 1000)
        
        # Check for key HTML elements
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('leaflet', html.lower())
        self.assertIn('Test Map', html)
        self.assertIn('marker', html.lower())
        
        # Check that provider data is included
        for provider in self.providers[:5]:
            if 'name' in provider:
                self.assertIn(provider['name'], html)
        
    def test_generate_html_map_with_empty_providers(self):
        """Test HTML map generation with empty providers list"""
        html = self.map_integration.generate_html_map(
            [],
            center_lat=self.test_lat,
            center_lon=self.test_lon
        )
        
        self.assertIsNotNone(html)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('0 providers', html)
        
    def test_generate_html_map_without_center(self):
        """Test HTML map generation without center coordinates"""
        html = self.map_integration.generate_html_map(
            self.providers,
            center_lat=None,
            center_lon=None
        )
        
        self.assertIsNotNone(html)
        # Should use average of provider coordinates
        self.assertIn(str(self.providers[0]['latitude'])[:5], html)
        
    def test_generate_html_map_dark_mode(self):
        """Test HTML map generation with dark mode"""
        html = self.map_integration.generate_html_map(
            self.providers,
            dark_mode=True
        )
        
        self.assertIsNotNone(html)
        # Check for dark mode indicators
        self.assertIn('dark', html.lower())
        self.assertIn('cartocdn', html)
        
    def test_generate_html_map_with_clustering(self):
        """Test HTML map generation with clustering enabled"""
        html = self.map_integration.generate_html_map(
            self.providers,
            cluster=True
        )
        
        self.assertIsNotNone(html)
        # Check for clustering code
        self.assertIn('markercluster', html.lower())
        self.assertIn('clusterGroup', html)
        
    def test_generate_html_map_without_clustering(self):
        """Test HTML map generation without clustering"""
        html = self.map_integration.generate_html_map(
            self.providers,
            cluster=False
        )
        
        self.assertIsNotNone(html)
        # Clustering code should not be present
        self.assertNotIn('markercluster', html.lower())
        
    def test_generate_html_map_with_controls(self):
        """Test HTML map generation with controls"""
        html = self.map_integration.generate_html_map(
            self.providers,
            include_controls=True
        )
        
        self.assertIsNotNone(html)
        # Check for control elements
        self.assertIn('categoryFilter', html)
        self.assertIn('searchInput', html)
        
    def test_generate_html_map_without_controls(self):
        """Test HTML map generation without controls"""
        html = self.map_integration.generate_html_map(
            self.providers,
            include_controls=False
        )
        
        self.assertIsNotNone(html)
        # Controls should not be present
        self.assertNotIn('categoryFilter', html)
        
    def test_generate_provider_heatmap(self):
        """Test heatmap generation"""
        html = self.map_integration.generate_provider_heatmap(
            self.providers,
            center_lat=self.test_lat,
            center_lon=self.test_lon,
            zoom=12,
            radius=25,
            blur=15
        )
        
        self.assertIsNotNone(html)
        self.assertIsInstance(html, str)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('leaflet-heat', html)
        self.assertIn('heatmap', html.lower())
        
    def test_generate_provider_heatmap_without_center(self):
        """Test heatmap generation without center coordinates"""
        html = self.map_integration.generate_provider_heatmap(
            self.providers,
            center_lat=None,
            center_lon=None
        )
        
        self.assertIsNotNone(html)
        # Should use average of provider coordinates
        self.assertIn(str(self.providers[0]['latitude'])[:5], html)
        
    def test_generate_provider_heatmap_empty_providers(self):
        """Test heatmap generation with empty providers list"""
        html = self.map_integration.generate_provider_heatmap(
            [],
            center_lat=self.test_lat,
            center_lon=self.test_lon
        )
        
        self.assertIsNotNone(html)
        self.assertIn('0 providers', html)
        
    def test_generate_route_map(self):
        """Test route map generation"""
        start_lat, start_lon = 40.7128, -74.0060
        end_lat, end_lon = 40.7589, -73.9851
        
        html = self.map_integration.generate_route_map(
            start_lat, start_lon,
            end_lat, end_lon,
            providers=self.providers[:5],
            title="Test Route"
        )
        
        self.assertIsNotNone(html)
        self.assertIsInstance(html, str)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('Test Route', html)
        self.assertIn('polyline', html)
        self.assertIn(str(start_lat), html)
        self.assertIn(str(end_lat), html)
        
    def test_generate_route_map_without_providers(self):
        """Test route map generation without providers"""
        start_lat, start_lon = 40.7128, -74.0060
        end_lat, end_lon = 40.7589, -73.9851
        
        html = self.map_integration.generate_route_map(
            start_lat, start_lon,
            end_lat, end_lon,
            providers=None
        )
        
        self.assertIsNotNone(html)
        self.assertIn('<!DOCTYPE html>', html)
        self.assertIn('polyline', html)
        
    def test_save_map_to_file(self):
        """Test saving HTML map to file"""
        html = self.map_integration.generate_html_map(
            self.providers,
            title="Test Save"
        )
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            filepath = self.map_integration.save_map_to_file(html, tmp.name)
            
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue(filepath.endswith('.html'))
        
        # Check file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            self.assertIn('Test Save', content)
        
        # Clean up
        os.unlink(filepath)
        
    def test_save_map_to_file_default_filename(self):
        """Test saving map with default filename"""
        html = self.map_integration.generate_html_map(self.providers)
        filepath = self.map_integration.save_map_to_file(html)
        
        self.assertIsNotNone(filepath)
        self.assertTrue(os.path.exists(filepath))
        self.assertTrue('service_providers_map.html' in filepath or filepath.endswith('.html'))
        
        # Clean up
        if os.path.exists(filepath):
            os.unlink(filepath)
            
    def test_save_map_to_file_custom_directory(self):
        """Test saving map to custom directory"""
        html = self.map_integration.generate_html_map(self.providers)
        
        # Create a custom directory
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_path = os.path.join(tmpdir, 'test_map.html')
            filepath = self.map_integration.save_map_to_file(html, custom_path)
            
            self.assertTrue(os.path.exists(filepath))
            self.assertEqual(filepath, os.path.abspath(custom_path))
            
    def test_show_map(self):
        """Test showing map in browser"""
        html = self.map_integration.generate_html_map(self.providers)
        
        # Mock webbrowser.open
        with patch('webbrowser.open') as mock_open:
            filepath = self.map_integration.show_map(html, open_browser=True)
            mock_open.assert_called_once()
            self.assertTrue(os.path.exists(filepath))
            
            # Clean up
            if os.path.exists(filepath):
                os.unlink(filepath)
                
    def test_show_map_without_browser(self):
        """Test showing map without opening browser"""
        html = self.map_integration.generate_html_map(self.providers)
        
        with patch('webbrowser.open') as mock_open:
            filepath = self.map_integration.show_map(html, open_browser=False)
            mock_open.assert_not_called()
            self.assertTrue(os.path.exists(filepath))
            
            # Clean up
            if os.path.exists(filepath):
                os.unlink(filepath)
                
    def test_create_provider_map(self):
        """Test creating a provider map"""
        with patch('webbrowser.open'):
            filepath = self.map_integration.create_provider_map(
                self.providers,
                show_browser=False,
                title="Test Provider Map"
            )
            
            self.assertIsNotNone(filepath)
            self.assertTrue(os.path.exists(filepath))
            self.assertTrue(filepath.endswith('.html'))
            
            # Check file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test Provider Map', content)
            
            # Clean up
            if os.path.exists(filepath):
                os.unlink(filepath)
                
    def test_create_heatmap(self):
        """Test creating a heatmap"""
        with patch('webbrowser.open'):
            filepath = self.map_integration.create_heatmap(
                self.providers,
                show_browser=False,
                radius=30,
                blur=20
            )
            
            self.assertIsNotNone(filepath)
            self.assertTrue(os.path.exists(filepath))
            self.assertTrue('heatmap.html' in filepath or filepath.endswith('.html'))
            
            # Check file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('heatmap', content.lower())
            
            # Clean up
            if os.path.exists(filepath):
                os.unlink(filepath)
                
    def test_create_route_map(self):
        """Test creating a route map"""
        with patch('webbrowser.open'):
            filepath = self.map_integration.create_route_map(
                40.7128, -74.0060,
                40.7589, -73.9851,
                providers=self.providers[:5],
                show_browser=False,
                title="Test Route Map"
            )
            
            self.assertIsNotNone(filepath)
            self.assertTrue(os.path.exists(filepath))
            
            # Check file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Test Route Map', content)
            
            # Clean up
            if os.path.exists(filepath):
                os.unlink(filepath)
                
    def test_get_map_statistics(self):
        """Test getting map statistics"""
        stats = self.map_integration.get_map_statistics(self.providers)
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats['total'], len(self.providers))
        self.assertIn('categories', stats)
        self.assertIn('avg_rating', stats)
        self.assertIn('available', stats)
        self.assertIn('unavailable', stats)
        self.assertIn('price_ranges', stats)
        self.assertIn('bounds', stats)
        
        # Check bounds
        bounds = stats['bounds']
        self.assertIsNotNone(bounds['min_lat'])
        self.assertIsNotNone(bounds['max_lat'])
        self.assertIsNotNone(bounds['min_lon'])
        self.assertIsNotNone(bounds['max_lon'])
        
    def test_get_map_statistics_empty(self):
        """Test getting map statistics with empty list"""
        stats = self.map_integration.get_map_statistics([])
        
        self.assertEqual(stats['total'], 0)
        self.assertEqual(stats['categories'], [])
        self.assertEqual(stats['avg_rating'], 0)
        self.assertEqual(stats['available'], 0)
        self.assertEqual(stats['unavailable'], 0)
        self.assertEqual(stats['price_ranges'], {})
        self.assertIsNone(stats['bounds']['min_lat'])
        
    def test_get_map_statistics_with_specific_providers(self):
        """Test getting map statistics with specific provider data"""
        test_providers = [
            {
                'category': 'Plumber',
                'rating': 4.8,
                'available': True,
                'price_range': '$$',
                'latitude': 40.7128,
                'longitude': -74.0060
            },
            {
                'category': 'Electrician',
                'rating': 4.5,
                'available': False,
                'price_range': '$$$',
                'latitude': 40.7589,
                'longitude': -73.9851
            }
        ]
        
        stats = self.map_integration.get_map_statistics(test_providers)
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(len(stats['categories']), 2)
        self.assertEqual(stats['avg_rating'], 4.65)
        self.assertEqual(stats['available'], 1)
        self.assertEqual(stats['unavailable'], 1)
        self.assertEqual(stats['price_ranges']['$$'], 1)
        self.assertEqual(stats['price_ranges']['$$$'], 1)
        
    def test_create_compare_map(self):
        """Test creating a comparison map"""
        primary_providers = self.providers[:5]
        compare_providers = self.providers[5:10]
        
        with patch('webbrowser.open'):
            filepath = self.map_integration.create_compare_map(
                primary_providers,
                compare_providers,
                show_browser=False
            )
            
            self.assertIsNotNone(filepath)
            self.assertTrue(os.path.exists(filepath))
            self.assertTrue('compare_map.html' in filepath or filepath.endswith('.html'))
            
            # Check file content
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('Primary', content)
                self.assertIn('Comparison', content)
            
            # Clean up
            if os.path.exists(filepath):
                os.unlink(filepath)
                
    def test_get_map_url(self):
        """Test getting map URL"""
        url = self.map_integration.get_map_url(
            self.providers[:5],
            center_lat=self.test_lat,
            center_lon=self.test_lon,
            zoom=13
        )
        
        self.assertIsNotNone(url)
        self.assertIsInstance(url, str)
        self.assertIn('openstreetmap', url.lower())
        self.assertIn(str(self.test_lat)[:5], url)
        
    def test_get_map_url_without_center(self):
        """Test getting map URL without center coordinates"""
        url = self.map_integration.get_map_url(
            self.providers[:5],
            center_lat=None,
            center_lon=None
        )
        
        self.assertIsNotNone(url)
        self.assertIn('openstreetmap', url.lower())
        
    def test_get_map_url_empty_providers(self):
        """Test getting map URL with empty providers list"""
        url = self.map_integration.get_map_url(
            [],
            center_lat=self.test_lat,
            center_lon=self.test_lon
        )
        
        self.assertIsNotNone(url)
        self.assertIn('openstreetmap', url.lower())
        
    def test_generate_static_map_image(self):
        """Test static map image generation (should raise NotImplementedError)"""
        with self.assertRaises(NotImplementedError):
            self.map_integration.generate_static_map_image(
                self.providers,
                width=600,
                height=400
            )
            
    def test_html_includes_provider_data(self):
        """Test that provider data is properly included in HTML"""
        html = self.map_integration.generate_html_map(
            self.providers,
            title="Data Test"
        )
        
        # Check that provider names are in the HTML
        for provider in self.providers[:3]:
            self.assertIn(provider['name'], html)
            
        # Check that provider coordinates are in the HTML
        for provider in self.providers[:3]:
            self.assertIn(str(provider['latitude'])[:6], html)
            self.assertIn(str(provider['longitude'])[:6], html)
            
    def test_html_includes_user_location(self):
        """Test that user location is included in HTML"""
        user_lat, user_lon = 40.7128, -74.0060
        
        html = self.map_integration.generate_html_map(
            self.providers,
            user_location=(user_lat, user_lon)
        )
        
        self.assertIn(str(user_lat), html)
        self.assertIn(str(user_lon), html)
        self.assertIn('userLat', html)
        self.assertIn('userLon', html)
        
    def test_html_responsive_design(self):
        """Test that HTML includes responsive design elements"""
        html = self.map_integration.generate_html_map(self.providers)
        
        self.assertIn('viewport', html)
        self.assertIn('@media', html)
        self.assertIn('max-width', html)
        
    def test_html_with_custom_dimensions(self):
        """Test HTML map with custom dimensions"""
        html = self.map_integration.generate_html_map(
            self.providers,
            width=800,
            height=600
        )
        
        self.assertIn('width: 800px', html)
        self.assertIn('height: 600px', html)
        
    def test_category_colors_completeness(self):
        """Test that all categories have colors defined"""
        for category in self.generator.categories:
            color = self.map_integration._get_category_color(category)
            self.assertIsNotNone(color)
            self.assertIsInstance(color, str)
            self.assertTrue(color.startswith('#'))
            
    def test_category_icons_completeness(self):
        """Test that all categories have icons defined"""
        for category in self.generator.categories:
            icon = self.map_integration._get_category_icon(category)
            self.assertIsNotNone(icon)
            self.assertIsInstance(icon, str)
            
    def test_html_cluster_code_generation(self):
        """Test cluster code generation"""
        # Test with clustering enabled
        html_with_cluster = self.map_integration.generate_html_map(
            self.providers,
            cluster=True
        )
        self.assertIn('markerClusterGroup', html_with_cluster)
        
        # Test with clustering disabled
        html_without_cluster = self.map_integration.generate_html_map(
            self.providers,
            cluster=False
        )
        self.assertNotIn('markerClusterGroup', html_without_cluster)
        
    def test_html_controls_code_generation(self):
        """Test controls code generation"""
        # Test with controls enabled
        html_with_controls = self.map_integration.generate_html_map(
            self.providers,
            include_controls=True
        )
        self.assertIn('categoryFilter', html_with_controls)
        self.assertIn('searchInput', html_with_controls)
        
        # Test with controls disabled
        html_without_controls = self.map_integration.generate_html_map(
            self.providers,
            include_controls=False
        )
        self.assertNotIn('categoryFilter', html_without_controls)
        
    def test_map_initialization_script(self):
        """Test that map initialization script is present"""
        html = self.map_integration.generate_html_map(self.providers)
        
        self.assertIn('const map = L.map', html)
        self.assertIn('L.tileLayer', html)
        self.assertIn('L.marker', html)
        
    def test_provider_popup_content(self):
        """Test that provider popup content includes all fields"""
        html = self.map_integration.generate_html_map(
            self.providers,
            title="Popup Test"
        )
        
        # Check for popup content elements
        self.assertIn('popup-content', html)
        self.assertIn('rating', html.lower())
        self.assertIn('category', html.lower())
        self.assertIn('address', html.lower())
        
    def test_legend_generation(self):
        """Test that legend is generated correctly"""
        html = self.map_integration.generate_html_map(self.providers)
        
        self.assertIn('legend', html)
        self.assertIn('Categories', html)
        
        # Check for category names in legend
        categories = set()
        for provider in self.providers[:5]:
            if 'category' in provider:
                categories.add(provider['category'])
                
        for category in list(categories)[:3]:
            self.assertIn(category, html)
            
    def test_html_validity(self):
        """Test basic HTML validity"""
        html = self.map_integration.generate_html_map(self.providers)
        
        # Check for balanced tags
        self.assertEqual(html.count('<div'), html.count('</div>'))
        self.assertEqual(html.count('<script'), html.count('</script>'))
        self.assertEqual(html.count('<style'), html.count('</style>'))
        
        # Check for proper HTML structure
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertTrue('<html' in html)
        self.assertTrue('<head>' in html)
        self.assertTrue('<body>' in html)
        self.assertTrue('</body>' in html)
        self.assertTrue('</html>' in html)
        
    def test_multiple_maps_generation(self):
        """Test generating multiple maps sequentially"""
        for i in range(3):
            html = self.map_integration.generate_html_map(
                self.providers,
                title=f"Test Map {i}"
            )
            self.assertIsNotNone(html)
            self.assertIn(f"Test Map {i}", html)


class TestMapIntegrationIntegration(unittest.TestCase):
    """Integration tests for MapIntegration with LocationService"""
    
    def setUp(self):
        """Set up integration test fixtures"""
        self.location_service = LocationService()
        self.map_integration = MapIntegration(self.location_service)
        self.providers = self.location_service.get_mock_providers()
        
    def test_integration_with_location_service(self):
        """Test integration between MapIntegration and LocationService"""
        # Get providers from location service
        providers = self.location_service.get_mock_providers()
        
        # Generate map with these providers
        html = self.map_integration.generate_html_map(
            providers,
            user_location=self.location_service.get_current_location()
        )
        
        self.assertIsNotNone(html)
        self.assertIn(str(len(providers)), html)
        
        # Check that provider data is included
        for provider in providers[:3]:
            if 'name' in provider:
                self.assertIn(provider['name'], html)
                
    def test_integration_geocoding(self):
        """Test integration with geocoding"""
        # Geocode an address
        coords = self.location_service.geocode_address("New York")
        self.assertIsNotNone(coords)
        
        if coords:
            lat, lon = coords
            
            # Generate map centered on geocoded location
            html = self.map_integration.generate_html_map(
                self.providers,
                center_lat=lat,
                center_lon=lon
            )
            
            self.assertIsNotNone(html)
            self.assertIn(str(lat)[:5], html)
            
    def test_integration_nearby_search(self):
        """Test integration with nearby search"""
        # Get user location
        user_lat, user_lon = self.location_service.get_current_location()
        
        # Find nearby providers
        nearby = self.location_service.get_nearby_providers(
            self.providers,
            user_lat,
            user_lon,
            radius=10.0
        )
        
        self.assertGreater(len(nearby), 0)
        
        # Generate map with nearby providers
        html = self.map_integration.generate_html_map(
            nearby,
            user_location=(user_lat, user_lon),
            show_distance=True
        )
        
        self.assertIsNotNone(html)
        self.assertIn(str(len(nearby)), html)
        
    def test_integration_full_workflow(self):
        """Test complete workflow: search -> map -> display"""
        # 1. Get user location
        user_location = self.location_service.get_current_location()
        self.assertIsNotNone(user_location)
        user_lat, user_lon = user_location
        
        # 2. Search for providers
        providers = self.location_service.get_mock_providers()
        nearby = self.location_service.get_nearby_providers(
            providers,
            user_lat,
            user_lon,
            radius=5.0,
            category="Plumber"
        )
        
        # 3. Generate map
        html = self.map_integration.generate_html_map(
            nearby,
            user_location=(user_lat, user_lon),
            title=f"Nearby Plumbers ({len(nearby)})",
            cluster=True
        )
        
        self.assertIsNotNone(html)
        self.assertIn('Nearby Plumbers', html)
        
        # 4. Save map
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            filepath = self.map_integration.save_map_to_file(html, tmp.name)
            
        self.assertTrue(os.path.exists(filepath))
        
        # Clean up
        if os.path.exists(filepath):
            os.unlink(filepath)


class TestMapIntegrationPerformance(unittest.TestCase):
    """Performance tests for MapIntegration"""
    
    def setUp(self):
        """Set up performance test fixtures"""
        self.map_integration = MapIntegration()
        self.generator = SampleDataGenerator()
        
    def test_large_dataset_performance(self):
        """Test performance with large dataset"""
        import time
        
        # Generate large dataset
        providers = self.generator.generate_providers(count=100)
        
        # Measure HTML generation time
        start_time = time.time()
        html = self.map_integration.generate_html_map(
            providers,
            cluster=True,
            include_controls=True
        )
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # Should generate within reasonable time (< 2 seconds)
        self.assertLess(generation_time, 2.0)
        self.assertIsNotNone(html)
        
    def test_memory_usage_with_clustering(self):
        """Test memory usage with clustering enabled"""
        providers = self.generator.generate_providers(count=50)
        
        html_cluster = self.map_integration.generate_html_map(
            providers,
            cluster=True
        )
        
        html_no_cluster = self.map_integration.generate_html_map(
            providers,
            cluster=False
        )
        
        # Clustering should produce larger HTML due to additional scripts
        self.assertGreater(len(html_cluster), len(html_no_cluster))
        
    def test_html_size_with_different_provider_counts(self):
        """Test HTML size with different provider counts"""
        sizes = []
        counts = [10, 50, 100]
        
        for count in counts:
            providers = self.generator.generate_providers(count=count)
            html = self.map_integration.generate_html_map(providers)
            sizes.append(len(html))
            
        # Size should increase with provider count
        for i in range(1, len(sizes)):
            self.assertGreater(sizes[i], sizes[i-1])
            
    def test_serialization_performance(self):
        """Test performance of saving and loading maps"""
        import time
        
        providers = self.generator.generate_providers(count=50)
        html = self.map_integration.generate_html_map(providers)
        
        # Measure save time
        start_time = time.time()
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp:
            filepath = self.map_integration.save_map_to_file(html, tmp.name)
        save_time = time.time() - start_time
        
        self.assertLess(save_time, 0.5)
        
        # Clean up
        if os.path.exists(filepath):
            os.unlink(filepath)


if __name__ == '__main__':
    # Run all tests with increased verbosity
    unittest.main(verbosity=2)