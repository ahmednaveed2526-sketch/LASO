"""
Geographic Utilities Module
Member 3: Location & Search Module Developer
LASO App - Group 10

Provides utility functions for geographic calculations and data manipulation.
"""

import math
import re
from typing import Tuple, Optional, List, Dict, Any
from dataclasses import dataclass
from functools import lru_cache

@dataclass
class BoundingBox:
    """Represents a geographic bounding box"""
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get center point of bounding box"""
        return (
            (self.min_lat + self.max_lat) / 2,
            (self.min_lon + self.max_lon) / 2
        )
    
    @property
    def width(self) -> float:
        """Get width in degrees"""
        return self.max_lon - self.min_lon
    
    @property
    def height(self) -> float:
        """Get height in degrees"""
        return self.max_lat - self.min_lat


class GeoUtils:
    """Utility class for geographic calculations and conversions"""
    
    # Earth's circumference in kilometers
    EARTH_CIRCUMFERENCE_KM = 40075.0
    
    # Degree to radian conversion
    DEGREE_TO_RADIAN = math.pi / 180.0
    RADIAN_TO_DEGREE = 180.0 / math.pi
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """Convert degrees to radians"""
        return degrees * GeoUtils.DEGREE_TO_RADIAN
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """Convert radians to degrees"""
        return radians * GeoUtils.RADIAN_TO_DEGREE
    
    @staticmethod
    def km_to_miles(km: float) -> float:
        """Convert kilometers to miles"""
        return km * 0.621371
    
    @staticmethod
    def miles_to_km(miles: float) -> float:
        """Convert miles to kilometers"""
        return miles * 1.60934
    
    @staticmethod
    def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate great-circle distance using the Haversine formula.
        
        Args:
            lat1, lon1: First point coordinates in degrees
            lat2, lon2: Second point coordinates in degrees
        
        Returns:
            Distance in kilometers
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return GeoUtils.EARTH_CIRCUMFERENCE_KM / math.pi * c
    
    @staticmethod
    def vincenty_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance using Vincenty's formula (more accurate for long distances).
        
        Args:
            lat1, lon1: First point coordinates in degrees
            lat2, lon2: Second point coordinates in degrees
        
        Returns:
            Distance in kilometers
        """
        # WGS-84 ellipsoid parameters
        a = 6378.137  # Semi-major axis (km)
        f = 1 / 298.257223563  # Flattening
        b = a * (1 - f)  # Semi-minor axis (km)
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        L = lon2_rad - lon1_rad
        U1 = math.atan((1 - f) * math.tan(lat1_rad))
        U2 = math.atan((1 - f) * math.tan(lat2_rad))
        
        sinU1 = math.sin(U1)
        cosU1 = math.cos(U1)
        sinU2 = math.sin(U2)
        cosU2 = math.cos(U2)
        
        lambda_ = L
        lambda_old = 0
        iter_limit = 100
        
        while abs(lambda_ - lambda_old) > 1e-12 and iter_limit > 0:
            iter_limit -= 1
            sin_lambda = math.sin(lambda_)
            cos_lambda = math.cos(lambda_)
            
            sin_sigma = math.sqrt(
                (cosU2 * sin_lambda) ** 2 +
                (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda) ** 2
            )
            
            if sin_sigma == 0:
                return 0.0
            
            cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)
            
            sin_alpha = cosU1 * cosU2 * sin_lambda / sin_sigma
            cos2_alpha = 1 - sin_alpha ** 2
            cos2_sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos2_alpha if cos2_alpha != 0 else 0
            
            C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
            lambda_old = lambda_
            lambda_ = L + (1 - C) * f * sin_alpha * (
                sigma + C * sin_sigma * (
                    cos2_sigma_m + C * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2)
                )
            )
        
        if iter_limit <= 0:
            # Fallback to Haversine if Vincenty doesn't converge
            return GeoUtils.haversine_distance(lat1, lon1, lat2, lon2)
        
        u2 = cos2_alpha * (a ** 2 - b ** 2) / b ** 2
        A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
        
        delta_sigma = B * sin_sigma * (
            cos2_sigma_m + B / 4 * (
                cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) -
                B / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)
            )
        )
        
        return b * A * (sigma - delta_sigma)
    
    @staticmethod
    def get_bounding_box(lat: float, lon: float, radius_km: float) -> BoundingBox:
        """
        Calculate bounding box from center point and radius.
        
        Args:
            lat: Center latitude in degrees
            lon: Center longitude in degrees  
            radius_km: Radius in kilometers
        
        Returns:
            BoundingBox object
        """
        # Earth's radius in kilometers
        earth_radius = 6371.0
        
        # Approximate degrees per kilometer at given latitude
        lat_degrees_per_km = 1 / 111.32  # Approximately 111.32 km per degree
        lon_degrees_per_km = 1 / (111.32 * math.cos(math.radians(lat)))
        
        lat_offset = radius_km * lat_degrees_per_km
        lon_offset = radius_km * lon_degrees_per_km
        
        return BoundingBox(
            min_lat=lat - lat_offset,
            min_lon=lon - lon_offset,
            max_lat=lat + lat_offset,
            max_lon=lon + lon_offset
        )
    
    @staticmethod
    def is_point_in_box(lat: float, lon: float, box: BoundingBox) -> bool:
        """Check if a point is inside a bounding box"""
        return (
            box.min_lat <= lat <= box.max_lat and
            box.min_lon <= lon <= box.max_lon
        )
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """Validate geographic coordinates"""
        try:
            lat = float(lat)
            lon = float(lon)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (TypeError, ValueError):
            return False
    
    @staticmethod
    def normalize_coordinates(lat: float, lon: float) -> Tuple[float, float]:
        """Normalize coordinates to valid ranges"""
        # Normalize latitude
        lat = max(-90, min(90, lat))
        
        # Normalize longitude
        if lon > 180:
            lon = lon % 360
            if lon > 180:
                lon -= 360
        elif lon < -180:
            lon = lon % 360
            if lon < -180:
                lon += 360
        
        return lat, lon
    
    @staticmethod
    @lru_cache(maxsize=1000)
    def cache_geocode(address: str) -> Optional[Tuple[float, float]]:
        """Cached geocoding of addresses"""
        # This would be implemented with actual geocoding service
        # Using lru_cache for automatic caching
        pass
    
    @staticmethod
    def format_coordinates(lat: float, lon: float, format_type: str = "decimal") -> str:
        """Format coordinates for display"""
        if format_type == "decimal":
            return f"{lat:.6f}, {lon:.6f}"
        elif format_type == "dms":
            # Degrees, Minutes, Seconds
            lat_deg = int(abs(lat))
            lat_min = int((abs(lat) - lat_deg) * 60)
            lat_sec = ((abs(lat) - lat_deg - lat_min / 60) * 3600)
            
            lon_deg = int(abs(lon))
            lon_min = int((abs(lon) - lon_deg) * 60)
            lon_sec = ((abs(lon) - lon_deg - lon_min / 60) * 3600)
            
            lat_dir = 'N' if lat >= 0 else 'S'
            lon_dir = 'E' if lon >= 0 else 'W'
            
            return f"{lat_deg}°{lat_min}'{lat_sec:.1f}\"{lat_dir}, {lon_deg}°{lon_min}'{lon_sec:.1f}\"{lon_dir}"
        else:
            return f"{lat}, {lon}"
    
    @staticmethod
    def parse_coordinates(coord_str: str) -> Optional[Tuple[float, float]]:
        """Parse coordinates from various string formats"""
        # Remove whitespace
        coord_str = coord_str.strip()
        
        # Try to parse as decimal
        try:
            parts = re.findall(r'[-+]?\d*\.?\d+', coord_str)
            if len(parts) >= 2:
                return float(parts[0]), float(parts[1])
        except ValueError:
            pass
        
        # Try to parse DMS format
        dms_pattern = r'(\d+)°(\d+)\'([\d.]+)"([NS]),?\s*(\d+)°(\d+)\'([\d.]+)"([EW])'
        match = re.search(dms_pattern, coord_str)
        if match:
            lat_deg, lat_min, lat_sec, lat_dir, lon_deg, lon_min, lon_sec, lon_dir = match.groups()
            
            lat = float(lat_deg) + float(lat_min) / 60 + float(lat_sec) / 3600
            lon = float(lon_deg) + float(lon_min) / 60 + float(lon_sec) / 3600
            
            if lat_dir == 'S':
                lat = -lat
            if lon_dir == 'W':
                lon = -lon
            
            return lat, lon
        
        return None