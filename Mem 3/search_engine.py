"""
Advanced Search Engine Module
Member 3: Location & Search Module Developer
LASO App - Group 10

Provides intelligent search capabilities with filtering, sorting, and ranking.
"""

import re
import json
from typing import List, Dict, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import math

from geo_utils import GeoUtils
from config import Config


@dataclass
class SearchFilter:
    """Search filter criteria"""
    category: Optional[str] = None
    min_rating: Optional[float] = None
    max_price: Optional[str] = None
    min_experience: Optional[int] = None
    available_only: bool = True
    keywords: Optional[List[str]] = None
    sort_by: str = "distance"  # distance, rating, relevance, price
    sort_order: str = "asc"    # asc, desc


@dataclass
class SearchResult:
    """Individual search result with metadata"""
    provider: Dict[str, Any]
    distance: float = 0.0
    relevance_score: float = 0.0
    match_type: str = "exact"  # exact, partial, fuzzy
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.provider.copy()
        result.update({
            'distance': self.distance,
            'relevance_score': self.relevance_score,
            'match_type': self.match_type
        })
        return result


class SearchEngine:
    """
    Advanced search engine for finding service providers.
    
    Features:
    - Full-text search with relevance scoring
    - Multiple filter criteria (category, rating, price, etc.)
    - Intelligent ranking algorithms
    - Fuzzy matching for misspelled queries
    - Result caching for performance
    """
    
    def __init__(self, location_service=None):
        """
        Initialize search engine.
        
        Args:
            location_service: LocationService instance for distance calculations
        """
        self.location_service = location_service
        self._cache = {}
        self._search_history = []
        
        # Category keywords for relevance scoring
        self._category_keywords = {
            'plumber': ['plumbing', 'pipe', 'leak', 'water', 'drain', 'faucet', 'toilet'],
            'electrician': ['electrical', 'wiring', 'power', 'light', 'circuit', 'switch', 'socket'],
            'landscaper': ['landscape', 'garden', 'lawn', 'tree', 'plant', 'yard', 'grass'],
            'cleaner': ['clean', 'cleaning', 'house', 'maid', 'janitor', 'dust', 'vacuum'],
            'painter': ['paint', 'wall', 'color', 'coating', 'finish', 'brush', 'roller'],
            'handyman': ['repair', 'fix', 'maintenance', 'assembly', 'install', 'renovate'],
            'roofer': ['roof', 'shingle', 'tile', 'leak', 'repair', 'installation'],
            'hvac': ['heating', 'cooling', 'air', 'ventilation', 'ac', 'furnace', 'thermostat'],
            'mover': ['move', 'moving', 'relocation', 'pack', 'truck', 'hauling'],
            'carpenter': ['wood', 'carpentry', 'cabinet', 'furniture', 'joinery', 'saw'],
            'gardener': ['garden', 'plant', 'flower', 'tree', 'shrub', 'soil'],
            'pest_control': ['pest', 'insect', 'bug', 'rodent', 'exterminate', 'termite']
        }
        
        # Price level mapping
        self._price_levels = {
            '$': {'min': 0, 'max': 50},
            '$$': {'min': 50, 'max': 150},
            '$$$': {'min': 150, 'max': 500},
            '$$$$': {'min': 500, 'max': float('inf')}
        }
    
    def search(self, 
               query: str,
               providers: List[Dict],
               user_lat: Optional[float] = None,
               user_lon: Optional[float] = None,
               filters: Optional[SearchFilter] = None,
               limit: int = 20) -> List[SearchResult]:
        """
        Perform intelligent search across providers.
        
        Args:
            query: Search query string
            providers: List of provider dictionaries
            user_lat, user_lon: User location for distance calculation
            filters: Search filters
            limit: Maximum number of results
        
        Returns:
            List of SearchResult objects
        """
        # Generate cache key
        cache_key = self._generate_cache_key(query, user_lat, user_lon, filters)
        if cache_key in self._cache:
            return self._cache[cache_key][:limit]
        
        # Apply filters
        filtered_providers = self._apply_filters(providers, filters)
        
        # Score and rank results
        results = []
        for provider in filtered_providers:
            score = self._calculate_relevance_score(query, provider)
            
            # Add distance if location provided
            distance = 0.0
            if user_lat is not None and user_lon is not None and self.location_service:
                if 'latitude' in provider and 'longitude' in provider:
                    distance = self.location_service.calculate_distance(
                        user_lat, user_lon, 
                        provider['latitude'], provider['longitude']
                    )
            
            # Create result
            result = SearchResult(
                provider=provider,
                distance=distance,
                relevance_score=score,
                match_type=self._determine_match_type(query, provider)
            )
            results.append(result)
        
        # Sort results
        results = self._sort_results(results, filters)
        
        # Cache results
        self._cache[cache_key] = results
        
        # Record search history
        self._search_history.append({
            'query': query,
            'timestamp': datetime.now(),
            'result_count': len(results)
        })
        
        return results[:limit]
    
    def _apply_filters(self, providers: List[Dict], filters: Optional[SearchFilter]) -> List[Dict]:
        """Apply search filters to providers"""
        if not filters:
            return providers
        
        filtered = []
        
        for provider in providers:
            # Category filter
            if filters.category:
                if provider.get('category', '').lower() != filters.category.lower():
                    continue
            
            # Rating filter
            if filters.min_rating is not None:
                if provider.get('rating', 0) < filters.min_rating:
                    continue
            
            # Availability filter
            if filters.available_only:
                if not provider.get('available', True):
                    continue
            
            # Experience filter
            if filters.min_experience is not None:
                if provider.get('years_experience', 0) < filters.min_experience:
                    continue
            
            # Price filter
            if filters.max_price:
                provider_price = provider.get('price_range', '$')
                if not self._compare_price(provider_price, filters.max_price):
                    continue
            
            # Keyword filter
            if filters.keywords:
                if not self._keyword_match(provider, filters.keywords):
                    continue
            
            filtered.append(provider)
        
        return filtered
    
    def _calculate_relevance_score(self, query: str, provider: Dict) -> float:
        """Calculate relevance score for a provider"""
        if not query:
            return 0.0
        
        query = query.lower()
        score = 0.0
        
        # Check name match
        if 'name' in provider:
            name = provider['name'].lower()
            if query in name:
                score += 10.0
            elif any(word in name for word in query.split()):
                score += 5.0
        
        # Check description match
        if 'description' in provider:
            description = provider['description'].lower()
            if query in description:
                score += 3.0
            
            # Keyword matching
            query_words = query.split()
            for word in query_words:
                if word in description:
                    score += 0.5
        
        # Check category match
        if 'category' in provider:
            category = provider['category'].lower()
            if query in category:
                score += 8.0
            
            # Check category synonyms
            for key, keywords in self._category_keywords.items():
                if category in key or key in category:
                    for keyword in keywords:
                        if keyword in query:
                            score += 2.0
        
        # Rating bonus
        rating = provider.get('rating', 0)
        if rating >= Config.EXCELLENT_RATING:
            score += 2.0
        elif rating >= Config.GOOD_RATING:
            score += 1.0
        
        # Experience bonus
        experience = provider.get('years_experience', 0)
        if experience >= 10:
            score += 1.0
        elif experience >= 5:
            score += 0.5
        
        return round(score, 2)
    
    def _determine_match_type(self, query: str, provider: Dict) -> str:
        """Determine match type between query and provider"""
        query = query.lower()
        
        # Check exact match
        if 'name' in provider and provider['name'].lower() == query:
            return "exact"
        
        # Check partial match
        if 'name' in provider and query in provider['name'].lower():
            return "partial"
        
        # Check fuzzy match (word-level)
        if 'name' in provider:
            provider_words = set(provider['name'].lower().split())
            query_words = set(query.split())
            if len(provider_words.intersection(query_words)) > 0:
                return "fuzzy"
        
        return "partial"
    
    def _compare_price(self, provider_price: str, filter_price: str) -> bool:
        """Compare price ranges"""
        price_levels = {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
        provider_level = price_levels.get(provider_price, 0)
        filter_level = price_levels.get(filter_price, 0)
        
        return provider_level <= filter_level
    
    def _keyword_match(self, provider: Dict, keywords: List[str]) -> bool:
        """Check if provider matches keywords"""
        text = ' '.join([
            provider.get('name', ''),
            provider.get('description', ''),
            provider.get('category', '')
        ]).lower()
        
        for keyword in keywords:
            if keyword.lower() in text:
                return True
        
        return False
    
    def _sort_results(self, results: List[SearchResult], filters: Optional[SearchFilter]) -> List[SearchResult]:
        """Sort search results"""
        if not filters:
            sort_by = "relevance"
        else:
            sort_by = filters.sort_by
            sort_order = filters.sort_order
        
        if sort_by == "distance":
            results.sort(key=lambda x: x.distance)
        elif sort_by == "rating":
            results.sort(key=lambda x: x.provider.get('rating', 0), reverse=True)
        elif sort_by == "relevance":
            results.sort(key=lambda x: x.relevance_score, reverse=True)
        elif sort_by == "price":
            price_order = {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
            results.sort(
                key=lambda x: price_order.get(x.provider.get('price_range', '$'), 0),
                reverse=(sort_order == "desc")
            )
        elif sort_by == "experience":
            results.sort(
                key=lambda x: x.provider.get('years_experience', 0),
                reverse=(sort_order == "desc")
            )
        
        return results
    
    def _generate_cache_key(self, query: str, lat: Optional[float], lon: Optional[float], 
                           filters: Optional[SearchFilter]) -> str:
        """Generate cache key for search results"""
        key = f"{query}_{lat}_{lon}"
        if filters:
            key += f"_{json.dumps(filters.__dict__, sort_keys=True)}"
        return key
    
    def clear_cache(self) -> None:
        """Clear search cache"""
        self._cache.clear()
    
    def get_search_suggestions(self, query: str, providers: List[Dict], limit: int = 5) -> List[str]:
        """Get search suggestions based on query"""
        suggestions = []
        query = query.lower()
        
        for provider in providers:
            if 'name' in provider and query in provider['name'].lower():
                suggestions.append(provider['name'])
            if 'category' in provider and query in provider['category'].lower():
                suggestions.append(provider['category'])
        
        # Add category suggestions
        for category in Config.CATEGORIES:
            if query in category:
                suggestions.append(category)
        
        # Remove duplicates and sort
        suggestions = list(set(suggestions))
        suggestions.sort(key=len)  # Sort by length
        
        return suggestions[:limit]
    
    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """Get recent search history"""
        return self._search_history[-limit:]
    
    def get_popular_searches(self, limit: int = 5) -> List[str]:
        """Get most popular search queries"""
        query_counts = defaultdict(int)
        for entry in self._search_history:
            query_counts[entry['query']] += 1
        
        sorted_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
        return [query for query, _ in sorted_queries[:limit]]
    
    def get_filter_counts(self, providers: List[Dict]) -> Dict[str, Any]:
        """Get count of providers by different filters"""
        counts = {
            'total': len(providers),
            'categories': defaultdict(int),
            'price_ranges': defaultdict(int),
            'rating_brackets': {
                'excellent': 0,  # 4.5+
                'good': 0,       # 4.0-4.49
                'average': 0,    # 3.0-3.99
                'poor': 0        # < 3.0
            },
            'availability': {
                'available': 0,
                'unavailable': 0
            }
        }
        
        for provider in providers:
            # Category
            category = provider.get('category', 'uncategorized')
            counts['categories'][category] += 1
            
            # Price
            price = provider.get('price_range', '$')
            counts['price_ranges'][price] += 1
            
            # Rating
            rating = provider.get('rating', 0)
            if rating >= 4.5:
                counts['rating_brackets']['excellent'] += 1
            elif rating >= 4.0:
                counts['rating_brackets']['good'] += 1
            elif rating >= 3.0:
                counts['rating_brackets']['average'] += 1
            else:
                counts['rating_brackets']['poor'] += 1
            
            # Availability
            if provider.get('available', True):
                counts['availability']['available'] += 1
            else:
                counts['availability']['unavailable'] += 1
        
        return dict(counts)
    
    def fuzzy_search(self, query: str, providers: List[Dict], threshold: int = 70) -> List[Dict]:
        """
        Perform fuzzy search using Levenshtein distance.
        
        Args:
            query: Search query
            providers: List of providers
            threshold: Similarity threshold (0-100)
        
        Returns:
            List of matching providers
        """
        results = []
        query = query.lower()
        
        for provider in providers:
            name = provider.get('name', '').lower()
            similarity = self._calculate_similarity(query, name)
            
            if similarity >= threshold:
                results.append(provider)
        
        return results
    
    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """
        Calculate string similarity using Levenshtein distance.
        
        Returns:
            Similarity score (0-100)
        """
        if not s1 or not s2:
            return 0.0
        
        # Calculate Levenshtein distance
        def levenshtein_distance(a: str, b: str) -> int:
            if len(a) < len(b):
                a, b = b, a
            
            previous_row = list(range(len(b) + 1))
            for i, char_a in enumerate(a):
                current_row = [i + 1]
                for j, char_b in enumerate(b):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (char_a != char_b)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            
            return previous_row[-1]
        
        distance = levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        
        # Convert to percentage
        similarity = (1 - distance / max_len) * 100
        return similarity