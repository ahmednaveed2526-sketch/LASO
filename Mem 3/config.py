"""
Configuration Module for Location Service
Member 3: Location & Search Module Developer
LASO App - Group 10
"""

import os
from typing import Dict, Any

class Config:
    """Configuration settings for location services"""
    
    # Default settings
    DEFAULT_RADIUS_KM = 10.0
    DEFAULT_RADIUS_MILES = 6.2
    DEFAULT_UNIT = "km"  # km or miles
    MAX_SEARCH_RADIUS_KM = 100.0
    MIN_SEARCH_RADIUS_KM = 0.5
    
    # Earth constants
    EARTH_RADIUS_KM = 6371.0
    EARTH_RADIUS_MILES = 3959.0
    
    # Cache settings
    CACHE_TIMEOUT_SECONDS = 3600  # 1 hour
    CACHE_MAX_SIZE = 1000
    
    # Geocoding settings
    GEOCODING_PROVIDER = "mock"  # mock, google, openstreetmap
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
    OPENSTREETMAP_USER_AGENT = 'LASO-App/1.0'
    
    # Map settings
    MAP_TILE_PROVIDER = "openstreetmap"  # openstreetmap, google, mapbox
    MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN', '')
    DEFAULT_ZOOM_LEVEL = 13
    MIN_ZOOM_LEVEL = 3
    MAX_ZOOM_LEVEL = 19
    
    # Search settings
    MAX_SEARCH_RESULTS = 100
    DEFAULT_SEARCH_LIMIT = 20
    
    # Provider categories
    CATEGORIES = [
        "plumber",
        "electrician", 
        "landscaper",
        "cleaner",
        "painter",
        "handyman",
        "roofer",
        "hvac",
        "mover",
        "carpenter",
        "gardener",
        "pest_control",
        "locksmith",
        "tutor",
        "photographer",
        "event_planner",
        "fitness_trainer",
        "massage_therapist",
        "interior_designer",
        "architect"
    ]
    
    # Rating thresholds
    EXCELLENT_RATING = 4.5
    GOOD_RATING = 4.0
    AVERAGE_RATING = 3.0
    POOR_RATING = 2.0
    
    @classmethod
    def get_search_config(cls) -> Dict[str, Any]:
        """Get search configuration"""
        return {
            'default_radius': cls.DEFAULT_RADIUS_KM,
            'max_radius': cls.MAX_SEARCH_RADIUS_KM,
            'min_radius': cls.MIN_SEARCH_RADIUS_KM,
            'max_results': cls.MAX_SEARCH_RESULTS,
            'default_limit': cls.DEFAULT_SEARCH_LIMIT
        }
    
    @classmethod
    def get_map_config(cls) -> Dict[str, Any]:
        """Get map configuration"""
        return {
            'tile_provider': cls.MAP_TILE_PROVIDER,
            'default_zoom': cls.DEFAULT_ZOOM_LEVEL,
            'min_zoom': cls.MIN_ZOOM_LEVEL,
            'max_zoom': cls.MAX_ZOOM_LEVEL
        }