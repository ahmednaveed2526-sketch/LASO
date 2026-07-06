"""
Sample Data Generator for Location Module
Member 3: Location & Search Module Developer
LASO App - Group 10

This module provides comprehensive sample provider data with real coordinates,
categories, ratings, and other attributes for testing and demonstration purposes.
"""

import json
import random
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import math


class SampleDataGenerator:
    """
    Generate realistic sample data for service providers.
    
    Features:
    - Real geographic coordinates across multiple cities
    - Diverse service categories
    - Realistic ratings and reviews
    - Complete provider profiles
    - Data export to JSON/CSV
    """
    
    def __init__(self):
        """Initialize the sample data generator"""
        self.categories = [
            "Plumber", "Electrician", "Landscaper", "Cleaner", 
            "Painter", "Handyman", "Roofer", "HVAC", 
            "Mover", "Carpenter", "Gardener", "Pest Control",
            "Locksmith", "Tutor", "Photographer", "Event Planner",
            "Fitness Trainer", "Massage Therapist", "Interior Designer", "Architect"
        ]
        
        self.first_names = [
            "James", "Maria", "Robert", "Jennifer", "Michael", "Linda", 
            "William", "Elizabeth", "David", "Susan", "Richard", "Jessica",
            "Joseph", "Sarah", "Thomas", "Karen", "Charles", "Nancy",
            "Christopher", "Lisa", "Daniel", "Betty", "Matthew", "Helen",
            "Anthony", "Sandra", "Mark", "Donna", "Donald", "Carol"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia",
            "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson",
            "Martin", "Lee", "Perez", "Thompson", "White", "Harris",
            "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
        ]
        
        self.business_suffixes = [
            "Services", "Solutions", "Pro", "Experts", "Masters", 
            "Elite", "Premium", "Plus", "Direct", "Express",
            "Associates", "Group", "Team", "Works", "Crew"
        ]
        
        self.street_names = [
            "Main", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington",
            "Jefferson", "Adams", "Lincoln", "Park", "Lake", "Hill", "Forest",
            "River", "Valley", "Woodland", "Meadow", "Highland", "Sunset"
        ]
        
        self.street_suffixes = [
            "St", "Ave", "Blvd", "Rd", "Dr", "Ln", "Way", "Ct", "Pl", "Ter"
        ]
        
        self.cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix",
            "Philadelphia", "San Antonio", "San Diego", "Dallas", "Austin",
            "Jacksonville", "Fort Worth", "Columbus", "Charlotte", "San Francisco",
            "Indianapolis", "Seattle", "Denver", "Washington", "Boston",
            "El Paso", "Nashville", "Detroit", "Oklahoma City", "Portland",
            "Las Vegas", "Memphis", "Louisville", "Baltimore", "Milwaukee",
            "Albuquerque", "Tucson", "Fresno", "Sacramento", "Kansas City",
            "Long Beach", "Mesa", "Atlanta", "Colorado Springs", "Miami"
        ]
        
        self.state_abbr = [
            "NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "TX",
            "FL", "TX", "OH", "NC", "CA", "IN", "WA", "CO", "DC", "MA",
            "TX", "TN", "MI", "OK", "OR", "NV", "TN", "KY", "MD", "WI",
            "NM", "AZ", "CA", "CA", "MO", "CA", "AZ", "GA", "CO", "FL"
        ]
        
        self.zip_codes = [
            "10001", "90001", "60601", "77001", "85001", "19101", "78201",
            "92101", "75201", "78701", "32201", "76101", "43201", "28201",
            "94101", "46201", "98101", "80201", "20001", "02101", "79901",
            "37201", "48201", "73101", "97201", "89101", "38101", "40201",
            "21201", "53201", "87101", "85701", "93701", "94201", "64101",
            "90801", "85201", "30301", "80901", "33101"
        ]
        
        self.city_coordinates = {
            "New York": (40.7128, -74.0060),
            "Los Angeles": (34.0522, -118.2437),
            "Chicago": (41.8781, -87.6298),
            "Houston": (29.7604, -95.3698),
            "Phoenix": (33.4484, -112.0740),
            "Philadelphia": (39.9526, -75.1652),
            "San Antonio": (29.4241, -98.4936),
            "San Diego": (32.7157, -117.1611),
            "Dallas": (32.7767, -96.7970),
            "Austin": (30.2672, -97.7431),
            "Jacksonville": (30.3322, -81.6557),
            "Fort Worth": (32.7555, -97.3308),
            "Columbus": (39.9612, -82.9988),
            "Charlotte": (35.2271, -80.8431),
            "San Francisco": (37.7749, -122.4194),
            "Indianapolis": (39.7684, -86.1581),
            "Seattle": (47.6062, -122.3321),
            "Denver": (39.7392, -104.9903),
            "Washington": (38.9072, -77.0369),
            "Boston": (42.3601, -71.0589),
            "El Paso": (31.7619, -106.4850),
            "Nashville": (36.1627, -86.7816),
            "Detroit": (42.3314, -83.0458),
            "Oklahoma City": (35.4676, -97.5164),
            "Portland": (45.5152, -122.6784),
            "Las Vegas": (36.1699, -115.1398),
            "Memphis": (35.1495, -90.0490),
            "Louisville": (38.2527, -85.7585),
            "Baltimore": (39.2904, -76.6122),
            "Milwaukee": (43.0389, -87.9065),
            "Albuquerque": (35.0853, -106.6056),
            "Tucson": (32.2226, -110.9747),
            "Fresno": (36.7378, -119.7871),
            "Sacramento": (38.5816, -121.4944),
            "Kansas City": (39.0997, -94.5786),
            "Long Beach": (33.7701, -118.1937),
            "Mesa": (33.4152, -111.8315),
            "Atlanta": (33.7490, -84.3880),
            "Colorado Springs": (38.8339, -104.8214),
            "Miami": (25.7617, -80.1918)
        }
        
        self.category_descriptions = {
            "Plumber": [
                "Professional plumbing services with 24/7 emergency response",
                "Licensed plumber specializing in residential and commercial work",
                "Full-service plumbing company with 15+ years of experience",
                "Expert plumbing repairs, installations, and maintenance",
                "Reliable plumbing services with guaranteed satisfaction"
            ],
            "Electrician": [
                "Licensed electrician offering comprehensive electrical services",
                "Residential and commercial electrical work with safety guarantee",
                "Smart home installation and electrical system upgrades",
                "Emergency electrical services and system maintenance",
                "Professional electrical contracting with 20+ years experience"
            ],
            "Landscaper": [
                "Creative landscape design and installation services",
                "Sustainable landscaping with native plants and eco-friendly practices",
                "Professional lawn care, garden design, and maintenance",
                "Complete landscaping solutions from design to installation",
                "Expert tree care, irrigation, and outdoor lighting"
            ],
            "Cleaner": [
                "Eco-friendly cleaning services for residential and commercial spaces",
                "Professional deep cleaning with 100% satisfaction guarantee",
                "Regular and one-time cleaning services available",
                "Specialized cleaning for offices, homes, and events",
                "Trusted cleaning company with 10+ years of experience"
            ],
            "Painter": [
                "Professional interior and exterior painting services",
                "Expert color consultation and premium paint application",
                "Residential and commercial painting with quality guarantee",
                "Full-service painting including wallpaper and staining",
                "Detailed painting work with cleanup included"
            ],
            "Handyman": [
                "General handyman services for all home repairs and improvements",
                "Versatile handyman with expertise in multiple trades",
                "Fast and reliable repair services for homes and businesses",
                "Complete home maintenance and improvement solutions",
                "Professional handyman services with upfront pricing"
            ],
            "Roofer": [
                "Premium roofing services with lifetime workmanship warranty",
                "Expert roof installation, repair, and inspection services",
                "Commercial and residential roofing specialists",
                "Quality roof replacement and repair with premium materials",
                "Licensed roofing contractor with 18+ years experience"
            ],
            "HVAC": [
                "Heating, ventilation, and air conditioning services",
                "24/7 emergency HVAC repair and installation",
                "Energy-efficient HVAC solutions for homes and businesses",
                "Complete air quality and climate control services",
                "Professional HVAC maintenance and system replacement"
            ],
            "Mover": [
                "Professional moving services for local and long-distance moves",
                "Full-service moving with packing, loading, and storage",
                "Reliable and insured moving company",
                "Commercial and residential moving specialists",
                "Stress-free moving with experienced professionals"
            ],
            "Carpenter": [
                "Custom carpentry and woodworking services",
                "Expert furniture making, cabinetry, and restoration",
                "Detailed woodwork for residential and commercial spaces",
                "Precision carpentry with premium materials",
                "Complete joinery and finishing services"
            ]
        }
        
        self.service_examples = {
            "Plumber": [
                "emergency repair", "pipe installation", "drain cleaning",
                "water heater", "faucet repair", "toilet installation",
                "pipe replacement", "fixture installation"
            ],
            "Electrician": [
                "wiring", "lighting", "smart home", "panel upgrade",
                "outlet installation", "circuit repair", "home automation",
                "security lighting", "electrical inspection"
            ],
            "Landscaper": [
                "garden design", "lawn care", "tree planting", "irrigation",
                "hardscaping", "sod installation", "pruning", "mulching",
                "landscape lighting", "water features"
            ]
        }
        
        self.price_ranges = ['$', '$$', '$$$', '$$$$']
        self.ratings = [4.0, 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.0]
    
    def generate_provider(self, 
                         category: Optional[str] = None,
                         city: Optional[str] = None,
                         index: int = 0) -> Dict[str, Any]:
        """
        Generate a single provider with realistic data.
        
        Args:
            category: Specific category (random if None)
            city: Specific city (random if None)
            index: Index for uniqueness
        
        Returns:
            Provider dictionary
        """
        # Select category
        if category is None:
            category = random.choice(self.categories)
        
        # Select city
        if city is None:
            city = random.choice(list(self.city_coordinates.keys()))
        
        # Get base coordinates for city
        base_lat, base_lon = self.city_coordinates[city]
        
        # Add some randomness to coordinates (within ~5km)
        lat_offset = (random.random() - 0.5) * 0.05
        lon_offset = (random.random() - 0.5) * 0.05
        lat = base_lat + lat_offset
        lon = base_lon + lon_offset
        
        # Generate business name
        first_name = random.choice(self.first_names)
        last_name = random.choice(self.last_names)
        suffix = random.choice(self.business_suffixes)
        
        business_name_formats = [
            f"{first_name} {last_name} {suffix}",
            f"{category} {suffix}",
            f"{category} {suffix}",
            f"{first_name}'s {category}",
            f"Premier {category} {suffix}",
            f"Apex {category} {suffix}"
        ]
        
        name = random.choice(business_name_formats)
        
        # Generate address
        street_num = random.randint(100, 9999)
        street_name = random.choice(self.street_names)
        street_suffix = random.choice(self.street_suffixes)
        city_index = self.cities.index(city) if city in self.cities else 0
        state = self.state_abbr[city_index] if city_index < len(self.state_abbr) else "NY"
        zip_code = self.zip_codes[city_index] if city_index < len(self.zip_codes) else "10001"
        
        address = f"{street_num} {street_name} {street_suffix}, {city}, {state} {zip_code}"
        
        # Generate phone number
        area_code = random.randint(200, 999)
        exchange = random.randint(200, 999)
        subscriber = random.randint(1000, 9999)
        phone = f"+1-{area_code}-{exchange}-{subscriber}"
        
        # Generate email
        domain = random.choice(["gmail.com", "yahoo.com", "outlook.com", "protonmail.com", "icloud.com"])
        email = f"{first_name.lower()}.{last_name.lower()}@{domain}"
        website = f"www.{first_name.lower()}{last_name.lower()}.com"
        
        # Generate rating and reviews
        rating = random.choice(self.ratings)
        total_reviews = random.randint(10, 300)
        
        # Generate experience
        years_experience = random.randint(3, 25)
        
        # Generate price range
        price_range = random.choice(self.price_ranges)
        
        # Generate availability
        available = random.random() > 0.2  # 80% available
        
        # Get description
        descriptions = self.category_descriptions.get(category, ["Professional service provider"])
        description = random.choice(descriptions)
        
        # Get services
        services = self.service_examples.get(category, ["general service"])
        num_services = random.randint(3, 6)
        provider_services = random.sample(services, min(num_services, len(services)))
        
        # Generate opening hours
        opening_hours = {
            "Mon-Fri": f"{random.randint(6, 9)}am-{random.randint(6, 9)}pm",
            "Sat": f"{random.randint(7, 10)}am-{random.randint(4, 7)}pm",
            "Sun": random.choice(["Closed", f"{random.randint(8, 10)}am-{random.randint(2, 5)}pm"])
        }
        
        # Generate images (placeholder)
        images = [
            f"https://placehold.co/400x300/3498db/ffffff?text={category.replace(' ', '+')}"
        ]
        
        return {
            "id": index + 1,
            "name": name,
            "category": category,
            "description": description,
            "latitude": lat,
            "longitude": lon,
            "address": address,
            "phone": phone,
            "email": email,
            "website": website,
            "rating": round(rating, 1),
            "total_reviews": total_reviews,
            "years_experience": years_experience,
            "price_range": price_range,
            "available": available,
            "services": provider_services,
            "opening_hours": opening_hours,
            "images": images,
            "created_at": datetime.now().isoformat(),
            "city": city,
            "state": state,
            "zip_code": zip_code
        }
    
    def generate_providers(self, 
                          count: int = 50,
                          categories: Optional[List[str]] = None,
                          cities: Optional[List[str]] = None,
                          include_all_cities: bool = False) -> List[Dict[str, Any]]:
        """
        Generate multiple providers.
        
        Args:
            count: Number of providers to generate
            categories: Specific categories to include
            cities: Specific cities to include
            include_all_cities: Distribute across all cities
        
        Returns:
            List of provider dictionaries
        """
        providers = []
        
        if categories is None:
            categories = self.categories.copy()
        
        if include_all_cities:
            city_list = list(self.city_coordinates.keys())
        elif cities:
            city_list = cities
        else:
            city_list = [random.choice(list(self.city_coordinates.keys())) for _ in range(min(count, 10))]
        
        # Distribute providers across cities and categories
        for i in range(count):
            category = random.choice(categories)
            city = random.choice(city_list)
            provider = self.generate_provider(category=category, city=city, index=i)
            providers.append(provider)
        
        return providers
    
    def generate_nearby_providers(self, 
                                  center_lat: float,
                                  center_lon: float,
                                  radius_km: float = 10.0,
                                  count: int = 20,
                                  categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Generate providers within a specific radius of a location.
        
        Args:
            center_lat, center_lon: Center coordinates
            radius_km: Search radius in kilometers
            count: Number of providers to generate
            categories: Specific categories to include
        
        Returns:
            List of providers within radius
        """
        providers = []
        attempts = 0
        max_attempts = count * 3
        
        # Convert radius to degrees (approximate)
        radius_deg = radius_km / 111.0
        
        if categories is None:
            categories = self.categories.copy()
        
        while len(providers) < count and attempts < max_attempts:
            attempts += 1
            
            # Generate random point within radius
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius_deg)
            
            lat = center_lat + distance * math.cos(angle)
            lon = center_lon + distance * math.sin(angle)
            
            # Validate coordinates
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                continue
            
            # Find nearest city for address
            nearest_city = self._find_nearest_city(lat, lon)
            if nearest_city is None:
                continue
            
            # Generate provider at this location
            category = random.choice(categories)
            provider = self.generate_provider(category=category, city=nearest_city)
            provider['latitude'] = lat
            provider['longitude'] = lon
            provider['id'] = len(providers) + 1
            
            providers.append(provider)
        
        return providers
    
    def _find_nearest_city(self, lat: float, lon: float) -> Optional[str]:
        """Find the nearest city for a given coordinate."""
        min_distance = float('inf')
        nearest = None
        
        for city, coords in self.city_coordinates.items():
            city_lat, city_lon = coords
            distance = math.sqrt((lat - city_lat)**2 + (lon - city_lon)**2)
            if distance < min_distance:
                min_distance = distance
                nearest = city
        
        return nearest
    
    def generate_providers_by_category(self, 
                                      category: str, 
                                      count: int = 10,
                                      city: Optional[str] = None) -> List[Dict[str, Any]]:
        """Generate providers for a specific category."""
        providers = []
        for i in range(count):
            provider = self.generate_provider(category=category, city=city, index=i)
            providers.append(provider)
        return providers
    
    def generate_providers_by_city(self, 
                                  city: str, 
                                  count: int = 10,
                                  categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Generate providers in a specific city."""
        if categories is None:
            categories = self.categories.copy()
        
        providers = []
        for i in range(count):
            category = random.choice(categories)
            provider = self.generate_provider(category=category, city=city, index=i)
            providers.append(provider)
        return providers
    
    def generate_test_dataset(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a complete test dataset with organized categories.
        
        Returns:
            Dictionary with providers organized by category
        """
        dataset = {}
        
        for category in self.categories[:10]:  # Top 10 categories
            dataset[category] = self.generate_providers_by_category(
                category, 
                count=random.randint(5, 15)
            )
        
        return dataset
    
    def save_to_json(self, 
                     providers: List[Dict[str, Any]], 
                     filename: str = "sample_providers.json") -> str:
        """
        Save providers to a JSON file.
        
        Args:
            providers: List of provider dictionaries
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        # Convert datetime to string if needed
        data = []
        for p in providers:
            p_copy = p.copy()
            if 'created_at' in p_copy and isinstance(p_copy['created_at'], datetime):
                p_copy['created_at'] = p_copy['created_at'].isoformat()
            data.append(p_copy)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    def save_to_csv(self, 
                    providers: List[Dict[str, Any]], 
                    filename: str = "sample_providers.csv") -> str:
        """
        Save providers to a CSV file.
        
        Args:
            providers: List of provider dictionaries
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        import csv
        
        # Flatten nested structures
        flat_providers = []
        for p in providers:
            flat_p = p.copy()
            # Remove nested structures for CSV
            flat_p.pop('services', None)
            flat_p.pop('opening_hours', None)
            flat_p.pop('images', None)
            flat_p.pop('created_at', None)
            flat_providers.append(flat_p)
        
        if not flat_providers:
            return filename
        
        fieldnames = flat_providers[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(flat_providers)
        
        return filename
    
    def load_from_json(self, filename: str = "sample_providers.json") -> List[Dict[str, Any]]:
        """Load providers from a JSON file."""
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_statistics(self, providers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about a provider dataset."""
        if not providers:
            return {
                'total': 0,
                'categories': {},
                'avg_rating': 0,
                'price_ranges': {},
                'availability': {'available': 0, 'unavailable': 0},
                'cities': {},
                'total_reviews': 0
            }
        
        stats = {
            'total': len(providers),
            'categories': {},
            'price_ranges': {},
            'availability': {'available': 0, 'unavailable': 0},
            'cities': {},
            'total_reviews': 0,
            'avg_rating': 0
        }
        
        total_rating = 0
        
        for p in providers:
            category = p.get('category', 'Unknown')
            stats['categories'][category] = stats['categories'].get(category, 0) + 1
            
            price = p.get('price_range', '$')
            stats['price_ranges'][price] = stats['price_ranges'].get(price, 0) + 1
            
            if p.get('available', True):
                stats['availability']['available'] += 1
            else:
                stats['availability']['unavailable'] += 1
            
            city = p.get('city', 'Unknown')
            stats['cities'][city] = stats['cities'].get(city, 0) + 1
            
            stats['total_reviews'] += p.get('total_reviews', 0)
            total_rating += p.get('rating', 0)
        
        stats['avg_rating'] = total_rating / len(providers) if providers else 0
        
        return stats
    
    def print_summary(self, providers: List[Dict[str, Any]]) -> None:
        """Print a summary of the provider dataset."""
        stats = self.get_statistics(providers)
        
        print("=" * 60)
        print("📊 Provider Dataset Summary")
        print("=" * 60)
        print(f"\n📋 Total Providers: {stats['total']}")
        print(f"⭐ Average Rating: {stats['avg_rating']:.2f}")
        print(f"📝 Total Reviews: {stats['total_reviews']}")
        print(f"✅ Available: {stats['availability']['available']}")
        print(f"❌ Unavailable: {stats['availability']['unavailable']}")
        
        print("\n📂 Categories:")
        for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
            print(f"  - {category}: {count}")
        
        print("\n💵 Price Ranges:")
        for price, count in sorted(stats['price_ranges'].items()):
            print(f"  - {price}: {count}")
        
        print("\n🏙️ Cities:")
        for city, count in sorted(stats['cities'].items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  - {city}: {count}")
        
        print("\n" + "=" * 60)


# Convenience functions for quick data generation

def generate_sample_providers(count: int = 50) -> List[Dict[str, Any]]:
    """Generate sample providers."""
    generator = SampleDataGenerator()
    return generator.generate_providers(count=count)


def generate_providers_nearby(lat: float, lon: float, radius_km: float = 10.0, count: int = 20) -> List[Dict[str, Any]]:
    """Generate providers near a location."""
    generator = SampleDataGenerator()
    return generator.generate_nearby_providers(lat, lon, radius_km, count)


def get_test_providers() -> List[Dict[str, Any]]:
    """Get a small set of test providers."""
    generator = SampleDataGenerator()
    return generator.generate_providers(count=12)


def get_nyc_providers() -> List[Dict[str, Any]]:
    """Get providers in NYC area."""
    generator = SampleDataGenerator()
    return generator.generate_providers_by_city("New York", count=20)


def get_la_providers() -> List[Dict[str, Any]]:
    """Get providers in LA area."""
    generator = SampleDataGenerator()
    return generator.generate_providers_by_city("Los Angeles", count=20)


def get_plumbers() -> List[Dict[str, Any]]:
    """Get plumber providers."""
    generator = SampleDataGenerator()
    return generator.generate_providers_by_category("Plumber", count=10)


def get_providers_with_high_rating(min_rating: float = 4.5) -> List[Dict[str, Any]]:
    """Get providers with high ratings."""
    generator = SampleDataGenerator()
    all_providers = generator.generate_providers(count=100)
    return [p for p in all_providers if p.get('rating', 0) >= min_rating]


def get_providers_by_price_range(price_range: str = "$") -> List[Dict[str, Any]]:
    """Get providers by price range."""
    generator = SampleDataGenerator()
    all_providers = generator.generate_providers(count=100)
    return [p for p in all_providers if p.get('price_range', '') == price_range]


def get_available_providers() -> List[Dict[str, Any]]:
    """Get available providers."""
    generator = SampleDataGenerator()
    all_providers = generator.generate_providers(count=100)
    return [p for p in all_providers if p.get('available', True)]


if __name__ == "__main__":
    # Test the sample data generator
    print("=" * 70)
    print("🏗️ Sample Data Generator - Test Suite")
    print("=" * 70)
    
    # Initialize generator
    generator = SampleDataGenerator()
    print(f"\n✅ SampleDataGenerator initialized")
    print(f"📂 Available categories: {len(generator.categories)}")
    print(f"🏙️ Available cities: {len(generator.city_coordinates)}")
    
    # Test 1: Generate a single provider
    print("\n📋 Test 1: Generate Single Provider")
    print("-" * 40)
    provider = generator.generate_provider()
    print(f"  Name: {provider['name']}")
    print(f"  Category: {provider['category']}")
    print(f"  Location: ({provider['latitude']:.4f}, {provider['longitude']:.4f})")
    print(f"  Rating: {provider['rating']}")
    print(f"  Price: {provider['price_range']}")
    print(f"  Available: {provider['available']}")
    
    # Test 2: Generate multiple providers
    print("\n📋 Test 2: Generate Multiple Providers")
    print("-" * 40)
    providers = generator.generate_providers(count=20)
    print(f"  Generated {len(providers)} providers")
    
    # Test 3: Nearby providers
    print("\n📋 Test 3: Generate Nearby Providers")
    print("-" * 40)
    nearby = generator.generate_nearby_providers(40.7128, -74.0060, radius_km=5.0, count=15)
    print(f"  Generated {len(nearby)} providers within 5km of NYC")
    for p in nearby[:5]:
        distance = math.sqrt(
            (p['latitude'] - 40.7128)**2 + (p['longitude'] + 74.0060)**2
        ) * 111
        print(f"    • {p['name']} ({p['category']}) - {distance:.1f}km away")
    
    # Test 4: Category-specific
    print("\n📋 Test 4: Category-Specific Providers")
    print("-" * 40)
    plumbers = generator.generate_providers_by_category("Plumber", count=8)
    print(f"  Generated {len(plumbers)} plumbers")
    for p in plumbers:
        print(f"    • {p['name']} - {p['rating']} ★")
    
    # Test 5: City-specific
    print("\n📋 Test 5: City-Specific Providers")
    print("-" * 40)
    la_providers = generator.generate_providers_by_city("Los Angeles", count=10)
    print(f"  Generated {len(la_providers)} providers in Los Angeles")
    for p in la_providers[:5]:
        print(f"    • {p['name']} - {p['address']}")
    
    # Test 6: Statistics
    print("\n📋 Test 6: Dataset Statistics")
    print("-" * 40)
    stats = generator.get_statistics(providers)
    print(f"  Total: {stats['total']}")
    print(f"  Avg Rating: {stats['avg_rating']:.2f}")
    print(f"  Categories: {len(stats['categories'])}")
    print(f"  Cities: {len(stats['cities'])}")
    
    # Test 7: Save to JSON
    print("\n📋 Test 7: Save to JSON")
    print("-" * 40)
    json_file = generator.save_to_json(providers[:10], "test_providers.json")
    print(f"  Saved to: {json_file}")
    
    # Test 8: Load from JSON
    print("\n📋 Test 8: Load from JSON")
    print("-" * 40)
    loaded = generator.load_from_json("test_providers.json")
    print(f"  Loaded {len(loaded)} providers")
    
    # Test 9: Quick convenience functions
    print("\n📋 Test 9: Convenience Functions")
    print("-" * 40)
    
    test_providers = get_test_providers()
    print(f"  get_test_providers(): {len(test_providers)} providers")
    
    nyc_providers = get_nyc_providers()
    print(f"  get_nyc_providers(): {len(nyc_providers)} providers")
    
    la_providers = get_la_providers()
    print(f"  get_la_providers(): {len(la_providers)} providers")
    
    plumber_list = get_plumbers()
    print(f"  get_plumbers(): {len(plumber_list)} providers")
    
    high_rated = get_providers_with_high_rating()
    print(f"  get_providers_with_high_rating(): {len(high_rated)} providers")
    
    # Test 10: Print summary
    print("\n📋 Test 10: Print Summary")
    print("-" * 40)
    generator.print_summary(providers)
    
    # Clean up
    import os
    if os.path.exists("test_providers.json"):
        os.remove("test_providers.json")
        print("\n🧹 Cleaned up test files")
    
    print("\n" + "=" * 70)
    print("✅ All tests completed successfully!")
    print("=" * 70)