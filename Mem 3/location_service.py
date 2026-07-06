"""
Main Location Service Module
Member 3: Location & Search Module Developer
LASO App - Group 10

Provides comprehensive location-based services including:
- GPS location acquisition
- Distance calculation
- Nearby provider search
- Map integration
- Geocoding and reverse geocoding
"""

import math
import json
import time
from typing import List, Dict, Optional, Tuple, Any, Union
from datetime import datetime
from dataclasses import dataclass
import threading
import queue

from geo_utils import GeoUtils
from search_engine import SearchEngine, SearchFilter, SearchResult
from config import Config


class LocationService:
    """
    Main location service providing comprehensive location-based functionality.
    
    Features:
    - GPS/device location acquisition (mock with option for real implementation)
    - Distance calculation (Haversine and Vincenty formulas)
    - Nearby provider search with radius filtering
    - Geocoding (address to coordinates)
    - Reverse geocoding (coordinates to address)
    - Location caching for performance
    - Location validation and normalization
    
    Usage Example:
        >>> service = LocationService()
        >>> user_lat, user_lon = service.get_current_location()
        >>> providers = service.get_mock_providers()
        >>> nearby = service.get_nearby_providers(providers, user_lat, user_lon, radius=10.0)
    """
    
    def __init__(self, use_miles: bool = False, enable_gps: bool = False):
        """
        Initialize the Location Service.
        
        Args:
            use_miles: If True, distances returned in miles; otherwise kilometers.
            enable_gps: If True, enable GPS functionality (requires hardware).
        """
        self.use_miles = use_miles
        self.radius_unit = "miles" if use_miles else "km"
        self.enable_gps = enable_gps
        
        # Initialize components
        self.search_engine = SearchEngine(self)
        self._geocoding_cache = {}
        self._location_cache = {}
        self._gps_enabled = enable_gps
        
        # Load mock data
        self._mock_providers = self._load_mock_providers()
        
        # GPS simulation (for testing)
        self._simulated_location = None
        
        # Thread safety
        self._lock = threading.Lock()
        self._location_queue = queue.Queue()
        
        # Start GPS thread if enabled
        if self.enable_gps:
            self._start_gps_thread()
    
    def _load_mock_providers(self) -> List[Dict]:
        """Load comprehensive mock provider data with real coordinates"""
        return [
            # NYC Providers
            {
                "id": 1,
                "name": "Pro Plumbing Solutions",
                "category": "Plumber",
                "description": "24/7 emergency plumbing services. Licensed, bonded, and insured with 15 years of experience.",
                "latitude": 40.7589,
                "longitude": -73.9851,
                "address": "123 Main St, New York, NY 10001",
                "phone": "+1-555-0101",
                "email": "info@proplumbing.com",
                "website": "www.proplumbing.com",
                "rating": 4.8,
                "total_reviews": 127,
                "years_experience": 15,
                "price_range": "$$",
                "available": True,
                "services": ["emergency repair", "pipe installation", "drain cleaning", "water heater"],
                "opening_hours": {"Mon-Fri": "8am-8pm", "Sat": "9am-6pm", "Sun": "10am-4pm"}
            },
            {
                "id": 2,
                "name": "Bright Spark Electric",
                "category": "Electrician",
                "description": "Professional residential and commercial electrical services. Specializing in smart home installations.",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "address": "456 Broadway, New York, NY 10013",
                "phone": "+1-555-0102",
                "email": "info@brightspark.com",
                "website": "www.brightspark.com",
                "rating": 4.9,
                "total_reviews": 89,
                "years_experience": 20,
                "price_range": "$$$",
                "available": True,
                "services": ["wiring", "lighting", "smart home", "panel upgrade"],
                "opening_hours": {"Mon-Fri": "7am-7pm", "Sat": "8am-5pm", "Sun": "Closed"}
            },
            {
                "id": 3,
                "name": "Green Thumb Landscaping",
                "category": "Landscaper",
                "description": "Creating beautiful outdoor spaces with sustainable landscaping practices.",
                "latitude": 40.7549,
                "longitude": -73.9840,
                "address": "789 Park Ave, New York, NY 10022",
                "phone": "+1-555-0103",
                "email": "info@greenthumb.com",
                "website": "www.greenthumb.com",
                "rating": 4.6,
                "total_reviews": 203,
                "years_experience": 10,
                "price_range": "$$",
                "available": True,
                "services": ["garden design", "lawn care", "tree planting", "irrigation"],
                "opening_hours": {"Mon-Fri": "8am-6pm", "Sat": "8am-4pm", "Sun": "Closed"}
            },
            {
                "id": 4,
                "name": "Sparkle Cleaning Co",
                "category": "Cleaner",
                "description": "Eco-friendly residential and commercial cleaning services with guaranteed satisfaction.",
                "latitude": 40.7489,
                "longitude": -73.9920,
                "address": "321 5th Ave, New York, NY 10016",
                "phone": "+1-555-0104",
                "email": "info@sparkleclean.com",
                "website": "www.sparkleclean.com",
                "rating": 4.7,
                "total_reviews": 156,
                "years_experience": 8,
                "price_range": "$",
                "available": False,
                "services": ["deep cleaning", "regular cleaning", "move-in/out", "office cleaning"],
                "opening_hours": {"Mon-Fri": "7am-8pm", "Sat": "8am-6pm", "Sun": "9am-4pm"}
            },
            {
                "id": 5,
                "name": "A1 Painting Services",
                "category": "Painter",
                "description": "Professional interior and exterior painting with premium materials.",
                "latitude": 40.7650,
                "longitude": -73.9800,
                "address": "555 Madison Ave, New York, NY 10022",
                "phone": "+1-555-0105",
                "email": "info@a1painting.com",
                "website": "www.a1painting.com",
                "rating": 4.4,
                "total_reviews": 78,
                "years_experience": 12,
                "price_range": "$$",
                "available": True,
                "services": ["interior painting", "exterior painting", "wallpaper", "staining"],
                "opening_hours": {"Mon-Fri": "7am-6pm", "Sat": "8am-5pm", "Sun": "Closed"}
            },
            {
                "id": 6,
                "name": "Fix-It Handyman",
                "category": "Handyman",
                "description": "Your one-stop solution for all home repairs and maintenance needs.",
                "latitude": 40.7180,
                "longitude": -74.0050,
                "address": "777 Canal St, New York, NY 10013",
                "phone": "+1-555-0106",
                "email": "info@fixit.com",
                "website": "www.fixit.com",
                "rating": 4.2,
                "total_reviews": 45,
                "years_experience": 7,
                "price_range": "$",
                "available": True,
                "services": ["general repair", "assembly", "installation", "maintenance"],
                "opening_hours": {"Mon-Fri": "8am-8pm", "Sat": "9am-6pm", "Sun": "10am-4pm"}
            },
            {
                "id": 7,
                "name": "Elite Roofing Inc",
                "category": "Roofer",
                "description": "Premium roofing services with 18 years of experience and lifetime warranties.",
                "latitude": 40.7400,
                "longitude": -73.9900,
                "address": "111 8th Ave, New York, NY 10011",
                "phone": "+1-555-0107",
                "email": "info@eliteroofing.com",
                "website": "www.eliteroofing.com",
                "rating": 4.5,
                "total_reviews": 112,
                "years_experience": 18,
                "price_range": "$$$",
                "available": True,
                "services": ["roof installation", "roof repair", "inspection", "maintenance"],
                "opening_hours": {"Mon-Fri": "6am-6pm", "Sat": "7am-4pm", "Sun": "Closed"}
            },
            {
                "id": 8,
                "name": "Cool Breeze HVAC",
                "category": "HVAC",
                "description": "Heating, ventilation, and air conditioning services with 24/7 emergency response.",
                "latitude": 40.7300,
                "longitude": -73.9950,
                "address": "222 10th Ave, New York, NY 10011",
                "phone": "+1-555-0108",
                "email": "info@coolbreeze.com",
                "website": "www.coolbreeze.com",
                "rating": 4.8,
                "total_reviews": 167,
                "years_experience": 14,
                "price_range": "$$$",
                "available": True,
                "services": ["AC installation", "heating repair", "maintenance", "air quality"],
                "opening_hours": {"Mon-Fri": "7am-9pm", "Sat": "8am-6pm", "Sun": "9am-4pm"}
            },
            {
                "id": 9,
                "name": "Sunny Window Cleaners",
                "category": "Cleaner",
                "description": "Professional window cleaning for homes and businesses with streak-free guarantee.",
                "latitude": 40.7550,
                "longitude": -73.9780,
                "address": "333 Lexington Ave, New York, NY 10022",
                "phone": "+1-555-0109",
                "email": "info@sunnywindow.com",
                "website": "www.sunnywindow.com",
                "rating": 4.3,
                "total_reviews": 34,
                "years_experience": 5,
                "price_range": "$",
                "available": True,
                "services": ["window cleaning", "gutter cleaning", "pressure washing"],
                "opening_hours": {"Mon-Fri": "7am-6pm", "Sat": "8am-4pm", "Sun": "Closed"}
            },
            {
                "id": 10,
                "name": "Master Moving Services",
                "category": "Mover",
                "description": "Professional residential and commercial moving with full packing services.",
                "latitude": 40.7250,
                "longitude": -73.9850,
                "address": "444 14th St, New York, NY 10011",
                "phone": "+1-555-0110",
                "email": "info@mastermoving.com",
                "website": "www.mastermoving.com",
                "rating": 4.1,
                "total_reviews": 56,
                "years_experience": 9,
                "price_range": "$$",
                "available": False,
                "services": ["local moving", "long distance", "packing", "storage"],
                "opening_hours": {"Mon-Fri": "7am-8pm", "Sat": "8am-6pm", "Sun": "9am-4pm"}
            },
            {
                "id": 11,
                "name": "Precision Carpentry",
                "category": "Carpenter",
                "description": "Custom carpentry, woodworking, and furniture making with premium craftsmanship.",
                "latitude": 40.7700,
                "longitude": -73.9700,
                "address": "555 1st Ave, New York, NY 10028",
                "phone": "+1-555-0111",
                "email": "info@precisioncarpentry.com",
                "website": "www.precisioncarpentry.com",
                "rating": 4.9,
                "total_reviews": 89,
                "years_experience": 22,
                "price_range": "$$$",
                "available": True,
                "services": ["custom furniture", "cabinetry", "woodwork", "restoration"],
                "opening_hours": {"Mon-Fri": "8am-6pm", "Sat": "9am-5pm", "Sun": "Closed"}
            },
            {
                "id": 12,
                "name": "Garden Oasis Landscaping",
                "category": "Landscaper",
                "description": "Creating breathtaking landscapes with sustainable, native plant designs.",
                "latitude": 40.7600,
                "longitude": -73.9600,
                "address": "666 3rd Ave, New York, NY 10022",
                "phone": "+1-555-0112",
                "email": "info@gardenoasis.com",
                "website": "www.gardenoasis.com",
                "rating": 4.6,
                "total_reviews": 123,
                "years_experience": 11,
                "price_range": "$$",
                "available": True,
                "services": ["landscape design", "installation", "maintenance", "lighting"],
                "opening_hours": {"Mon-Fri": "7am-7pm", "Sat": "8am-5pm", "Sun": "Closed"}
            },
            # Brooklyn providers
            {
                "id": 101,
                "name": "Brooklyn Plumbing Experts",
                "category": "Plumber",
                "description": "Professional plumbing services in Brooklyn with same-day service.",
                "latitude": 40.6782,
                "longitude": -73.9442,
                "address": "100 Atlantic Ave, Brooklyn, NY 11201",
                "phone": "+1-555-0201",
                "email": "info@bkplumbing.com",
                "rating": 4.7,
                "total_reviews": 34,
                "years_experience": 13,
                "price_range": "$$",
                "available": True,
                "services": ["emergency repair", "installation", "maintenance"],
                "opening_hours": {"Mon-Fri": "7am-8pm", "Sat": "8am-6pm", "Sun": "9am-4pm"}
            },
            {
                "id": 102,
                "name": "Brooklyn Electric",
                "category": "Electrician",
                "description": "Residential electrical services in Brooklyn and surrounding areas.",
                "latitude": 40.6900,
                "longitude": -73.9500,
                "address": "200 Court St, Brooklyn, NY 11231",
                "phone": "+1-555-0202",
                "email": "info@bkelectric.com",
                "rating": 4.5,
                "total_reviews": 28,
                "years_experience": 10,
                "price_range": "$$",
                "available": True,
                "services": ["wiring", "lighting", "panel upgrade"],
                "opening_hours": {"Mon-Fri": "8am-7pm", "Sat": "9am-5pm", "Sun": "Closed"}
            },
            # Queens providers
            {
                "id": 201,
                "name": "Queens Handyman Service",
                "category": "Handyman",
                "description": "General handyman services in Queens.",
                "latitude": 40.7282,
                "longitude": -73.7949,
                "address": "150 Queens Blvd, Queens, NY 11424",
                "phone": "+1-555-0301",
                "email": "info@queenshandyman.com",
                "rating": 4.3,
                "total_reviews": 19,
                "years_experience": 8,
                "price_range": "$",
                "available": True,
                "services": ["general repair", "assembly", "installation"],
                "opening_hours": {"Mon-Fri": "7am-8pm", "Sat": "8am-6pm", "Sun": "9am-4pm"}
            }
        ]
    
    def _start_gps_thread(self) -> None:
        """Start background thread for GPS location monitoring"""
        # This would be implemented with actual GPS hardware
        pass
    
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float, 
                          method: str = "haversine") -> float:
        """
        Calculate distance between two points.
        
        Args:
            lat1, lon1: First point coordinates in degrees
            lat2, lon2: Second point coordinates in degrees
            method: "haversine" or "vincenty"
        
        Returns:
            Distance in kilometers (or miles if use_miles is True)
        """
        # Validate coordinates
        if not GeoUtils.validate_coordinates(lat1, lon1) or not GeoUtils.validate_coordinates(lat2, lon2):
            raise ValueError("Invalid coordinates provided")
        
        # Calculate distance
        if method == "vincenty":
            distance_km = GeoUtils.vincenty_distance(lat1, lon1, lat2, lon2)
        else:
            distance_km = GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)
        
        # Convert to miles if needed
        if self.use_miles:
            return round(GeoUtils.km_to_miles(distance_km), 2)
        
        return round(distance_km, 2)
    
    def get_current_location(self) -> Optional[Tuple[float, float]]:
        """
        Get the current device location.
        
        Returns:
            Tuple of (latitude, longitude) or None if location unavailable
        """
        # If GPS is enabled, try to get real location
        if self.enable_gps:
            # In production, this would access GPS hardware
            # For now, return simulated location
            return self._get_simulated_location()
        
        # Return mocked location (New York City)
        return (40.7128, -74.0060)
    
    def _get_simulated_location(self) -> Optional[Tuple[float, float]]:
        """Get simulated location for testing"""
        if self._simulated_location:
            return self._simulated_location
        return (40.7128, -74.0060)  # NYC as default
    
    def set_simulated_location(self, lat: float, lon: float) -> None:
        """Set simulated location for testing"""
        if GeoUtils.validate_coordinates(lat, lon):
            self._simulated_location = (lat, lon)
        else:
            raise ValueError("Invalid coordinates for simulation")
    
    def get_nearby_providers(self, 
                            providers: List[Dict], 
                            user_lat: float, 
                            user_lon: float, 
                            radius: Optional[float] = None,
                            category: Optional[str] = None,
                            min_rating: Optional[float] = None,
                            limit: int = 20,
                            use_bbox: bool = True) -> List[Dict]:
        """
        Get providers within a specified radius of the user's location.
        
        Args:
            providers: List of provider dictionaries with location data
            user_lat: User's latitude
            user_lon: User's longitude
            radius: Search radius in kilometers (default: from config)
            category: Optional category filter
            min_rating: Optional minimum rating filter
            limit: Maximum number of results
            use_bbox: Use bounding box optimization
        
        Returns:
            List of providers within radius, sorted by distance
        """
        if radius is None:
            radius = Config.DEFAULT_RADIUS_KM
            if self.use_miles:
                radius = Config.DEFAULT_RADIUS_MILES
        
        # Use bounding box optimization for large provider lists
        if use_bbox and len(providers) > 100:
            box = GeoUtils.get_bounding_box(user_lat, user_lon, radius)
            providers = [p for p in providers if GeoUtils.is_point_in_box(
                p.get('latitude', 0), p.get('longitude', 0), box
            )]
        
        # Create search filter
        filter_obj = SearchFilter(
            category=category,
            min_rating=min_rating,
            available_only=True,
            sort_by="distance",
            sort_order="asc"
        )
        
        # Use search engine for filtering and sorting
        results = self.search_engine.search(
            "",  # Empty query for nearby search
            providers,
            user_lat,
            user_lon,
            filter_obj,
            limit
        )
        
        # Convert to list of dictionaries
        return [r.to_dict() for r in results]
    
    def get_providers_by_radius(self, 
                                providers: List[Dict],
                                user_lat: float,
                                user_lon: float,
                                radius_km: float,
                                include_distance: bool = True) -> List[Dict]:
        """
        Get providers within a specific radius.
        
        This is a more efficient version optimized for radius-only searches.
        """
        results = []
        radius_sq = radius_km ** 2
        
        # Use bounding box for initial filter
        box = GeoUtils.get_bounding_box(user_lat, user_lon, radius_km)
        
        for provider in providers:
            # Skip providers without location
            if 'latitude' not in provider or 'longitude' not in provider:
                continue
            
            lat = provider['latitude']
            lon = provider['longitude']
            
            # Quick bounding box check
            if not GeoUtils.is_point_in_box(lat, lon, box):
                continue
            
            # Calculate exact distance
            distance = self.calculate_distance(user_lat, user_lon, lat, lon)
            
            if distance <= radius_km:
                result = provider.copy()
                if include_distance:
                    result['distance'] = distance
                    result['distance_unit'] = self.radius_unit
                results.append(result)
        
        # Sort by distance
        results.sort(key=lambda x: x.get('distance', float('inf')))
        
        return results
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert an address to coordinates.
        
        Args:
            address: Street address or place name
        
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        # Check cache
        if address in self._geocoding_cache:
            return self._geocoding_cache[address]
        
        # Mock geocoding for demo
        mock_geocoding = {
            "new york": (40.7128, -74.0060),
            "nyc": (40.7128, -74.0060),
            "manhattan": (40.7831, -73.9712),
            "brooklyn": (40.6782, -73.9442),
            "queens": (40.7282, -73.7949),
            "bronx": (40.8448, -73.8648),
            "staten island": (40.5795, -74.1502),
            "jersey city": (40.7282, -74.0776),
            "newark": (40.7357, -74.1724),
            "philadelphia": (39.9526, -75.1652),
            "boston": (42.3601, -71.0589),
            "chicago": (41.8781, -87.6298),
            "los angeles": (34.0522, -118.2437),
            "san francisco": (37.7749, -122.4194),
            "seattle": (47.6062, -122.3321),
            "miami": (25.7617, -80.1918),
            "dallas": (32.7767, -96.7970),
            "houston": (29.7604, -95.3698),
            "atlanta": (33.7490, -84.3880),
            "washington": (38.9072, -77.0369),
            "denver": (39.7392, -104.9903),
            "las vegas": (36.1699, -115.1398),
            "orlando": (28.5383, -81.3792),
            "san diego": (32.7157, -117.1611)
        }
        
        # Try exact match
        address_lower = address.lower().strip()
        if address_lower in mock_geocoding:
            self._geocoding_cache[address] = mock_geocoding[address_lower]
            return mock_geocoding[address_lower]
        
        # Try partial match
        for key, coords in mock_geocoding.items():
            if key in address_lower or address_lower in key:
                self._geocoding_cache[address] = coords
                return coords
        
        return None
    
    def reverse_geocode(self, lat: float, lon: float) -> Optional[str]:
        """
        Convert coordinates to an address.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Address string or None if not found
        """
        # Mock reverse geocoding
        mock_reverse = {
            (40.7128, -74.0060): "New York, NY 10001",
            (40.7589, -73.9851): "New York, NY 10018",
            (40.7549, -73.9840): "New York, NY 10022",
            (40.7489, -73.9920): "New York, NY 10016",
            (40.6782, -73.9442): "Brooklyn, NY 11201",
            (40.7282, -73.7949): "Queens, NY 11424"
        }
        
        # Round to 4 decimal places for matching
        rounded_coords = (round(lat, 4), round(lon, 4))
        
        return mock_reverse.get(rounded_coords, None)
    
    def get_mock_providers(self) -> List[Dict]:
        """Get mock provider data for testing"""
        return self._mock_providers.copy()
    
    def set_providers(self, providers: List[Dict]) -> None:
        """Set the provider list for database integration"""
        self._mock_providers = providers
        self.search_engine.clear_cache()
    
    def search_providers(self, 
                        query: str,
                        user_lat: Optional[float] = None,
                        user_lon: Optional[float] = None,
                        category: Optional[str] = None,
                        min_rating: Optional[float] = None,
                        radius: Optional[float] = None,
                        limit: int = 20) -> List[Dict]:
        """
        Search providers with query and filters.
        
        Args:
            query: Search query
            user_lat, user_lon: User location
            category: Category filter
            min_rating: Minimum rating filter
            radius: Search radius
            limit: Maximum results
        
        Returns:
            List of matching providers
        """
        # Create search filter
        filter_obj = SearchFilter(
            category=category,
            min_rating=min_rating,
            available_only=True
        )
        
        # Get providers
        providers = self._mock_providers
        
        # Search
        results = self.search_engine.search(
            query,
            providers,
            user_lat,
            user_lon,
            filter_obj,
            limit
        )
        
        return [r.to_dict() for r in results]
    
    def get_provider_categories(self) -> List[str]:
        """Get list of all available provider categories"""
        categories = set()
        for provider in self._mock_providers:
            if 'category' in provider:
                categories.add(provider['category'])
        return sorted(list(categories))
    
    def get_providers_by_category(self, category: str) -> List[Dict]:
        """Get all providers in a specific category"""
        return [p for p in self._mock_providers 
                if p.get('category', '').lower() == category.lower()]
    
    def get_nearby_categories(self, user_lat: float, user_lon: float, radius: float = 10.0) -> Dict[str, int]:
        """Get count of providers by category within radius"""
        nearby = self.get_nearby_providers(self._mock_providers, user_lat, user_lon, radius)
        category_counts = {}
        
        for provider in nearby:
            category = provider.get('category', 'uncategorized')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def get_location_info(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get detailed location information"""
        info = {
            'coordinates': (lat, lon),
            'formatted': GeoUtils.format_coordinates(lat, lon),
            'address': self.reverse_geocode(lat, lon),
            'nearby_providers_count': 0,
            'categories': []
        }
        
        # Get nearby providers count and categories
        nearby = self.get_nearby_providers(self._mock_providers, lat, lon, radius=5.0)
        info['nearby_providers_count'] = len(nearby)
        
        categories = set()
        for provider in nearby:
            if 'category' in provider:
                categories.add(provider['category'])
        info['categories'] = list(categories)
        
        return info
    
    def clear_cache(self) -> None:
        """Clear all caches"""
        self._geocoding_cache.clear()
        self._location_cache.clear()
        self.search_engine.clear_cache()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            'total_providers': len(self._mock_providers),
            'categories': self.get_provider_categories(),
            'cache_size': len(self._geocoding_cache),
            'search_history_count': len(self.search_engine._search_history),
            'radius_unit': self.radius_unit,
            'gps_enabled': self.enable_gps,
            'timestamp': datetime.now().isoformat()
        }
    
    def update_provider_location(self, provider_id: int, lat: float, lon: float) -> bool:
        """Update a provider's location"""
        for provider in self._mock_providers:
            if provider.get('id') == provider_id:
                if GeoUtils.validate_coordinates(lat, lon):
                    provider['latitude'] = lat
                    provider['longitude'] = lon
                    self.search_engine.clear_cache()
                    return True
        return False
    
    def add_provider(self, provider: Dict) -> None:
        """Add a new provider"""
        # Generate ID if not provided
        if 'id' not in provider:
            max_id = max([p.get('id', 0) for p in self._mock_providers], default=0)
            provider['id'] = max_id + 1
        
        # Validate location
        if 'latitude' in provider and 'longitude' in provider:
            if not GeoUtils.validate_coordinates(provider['latitude'], provider['longitude']):
                raise ValueError("Invalid coordinates")
        
        self._mock_providers.append(provider)
        self.search_engine.clear_cache()
    
    def remove_provider(self, provider_id: int) -> bool:
        """Remove a provider by ID"""
        for i, provider in enumerate(self._mock_providers):
            if provider.get('id') == provider_id:
                self._mock_providers.pop(i)
                self.search_engine.clear_cache()
                return True
        return False


# Convenience functions for easy integration

def get_location_service(use_miles: bool = False, enable_gps: bool = False) -> LocationService:
    """Get a LocationService instance"""
    return LocationService(use_miles, enable_gps)


def get_nearby_providers_quick(providers: List[Dict], user_lat: float, user_lon: float, 
                               radius: float = 10.0) -> List[Dict]:
    """Quick function to get nearby providers"""
    service = LocationService()
    return service.get_nearby_providers(providers, user_lat, user_lon, radius)


if __name__ == "__main__":
    # Comprehensive test of location service
    print("=" * 70)
    print("LASO App - Location Service Test Suite")
    print("=" * 70)
    
    # Initialize service
    service = LocationService()
    print(f"\n✅ Location Service initialized (unit: {service.radius_unit})")
    
    # Get mock providers
    providers = service.get_mock_providers()
    print(f"📋 Loaded {len(providers)} mock providers")
    
    # Test 1: Distance Calculation
    print("\n📐 Test 1: Distance Calculation")
    print("-" * 40)
    test_coords = [
        ((40.7128, -74.0060), (40.7589, -73.9851)),
        ((40.7128, -74.0060), (40.7549, -73.9840)),
        ((40.7128, -74.0060), (40.6782, -73.9442))
    ]
    
    for (lat1, lon1), (lat2, lon2) in test_coords:
        dist = service.calculate_distance(lat1, lon1, lat2, lon2)
        print(f"  {lat1}, {lon1} -> {lat2}, {lon2}: {dist:.2f} {service.radius_unit}")
    
    # Test 2: Nearby Search
    print("\n📍 Test 2: Nearby Provider Search")
    print("-" * 40)
    user_lat, user_lon = 40.7128, -74.0060
    nearby = service.get_nearby_providers(providers, user_lat, user_lon, radius=5.0)
    
    print(f"  Found {len(nearby)} providers within 5 km:")
    for provider in nearby[:5]:
        print(f"    • {provider['name']} - {provider['distance']:.2f} km away")
    
    # Test 3: Category Filter
    print("\n🔍 Test 3: Category Filter")
    print("-" * 40)
    plumbers = service.get_nearby_providers(providers, user_lat, user_lon, 
                                           radius=10.0, category="plumber")
    print(f"  Found {len(plumbers)} plumbers within 10 km")
    for plumber in plumbers:
        print(f"    • {plumber['name']}")
    
    # Test 4: Search Engine
    print("\n🔎 Test 4: Search Functionality")
    print("-" * 40)
    search_results = service.search_providers("plumbing", user_lat, user_lon)
    print(f"  Found {len(search_results)} results for 'plumbing'")
    for result in search_results[:3]:
        relevance = result.get('relevance_score', 0)
        print(f"    • {result['name']} (Score: {relevance})")
    
    # Test 5: Geocoding
    print("\n🗺️ Test 5: Geocoding")
    print("-" * 40)
    test_addresses = ["New York", "Brooklyn", "Chicago", "Los Angeles"]
    for address in test_addresses:
        coords = service.geocode_address(address)
        if coords:
            print(f"  {address} -> ({coords[0]:.4f}, {coords[1]:.4f})")
        else:
            print(f"  {address} -> Not found")
    
    # Test 6: Location Info
    print("\n📊 Test 6: Location Information")
    print("-" * 40)
    info = service.get_location_info(40.7128, -74.0060)
    print(f"  Address: {info['address']}")
    print(f"  Nearby providers: {info['nearby_providers_count']}")
    print(f"  Categories available: {', '.join(info['categories'][:5])}")
    
    # Test 7: Statistics
    print("\n📈 Test 7: Service Statistics")
    print("-" * 40)
    stats = service.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed successfully!")
    print("=" * 70)