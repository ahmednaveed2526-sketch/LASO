"""
Map Integration Module
Member 3: Location & Search Module Developer
LASO App - Group 10

Provides map visualization and integration features:
- Generate interactive maps with provider locations
- Cluster markers for better performance
- Heatmaps for density visualization
- Integration with various map providers
- Route visualization between points
- Custom marker styling and popups
"""

import json
import webbrowser
import tempfile
import os
import math
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
from urllib.parse import urlencode

from geo_utils import GeoUtils
from config import Config


class MapIntegration:
    """
    Map integration service for visualizing providers and locations.
    
    Features:
    - Generate HTML maps with provider markers
    - Map clustering for many providers
    - Heatmap generation
    - Route visualization
    - Custom marker styling
    - Provider popup information
    - Category filtering on map
    - Distance display
    """
    
    def __init__(self, location_service=None):
        """
        Initialize map integration.
        
        Args:
            location_service: LocationService instance for data
        """
        self.location_service = location_service
        self._html_templates = {}
        self._map_cache = {}
        
        # Category colors for markers
        self.category_colors = {
            'plumber': '#3498db',
            'electrician': '#f1c40f',
            'landscaper': '#2ecc71',
            'cleaner': '#9b59b6',
            'painter': '#e67e22',
            'handyman': '#1abc9c',
            'roofer': '#e74c3c',
            'hvac': '#00bcd4',
            'mover': '#ff6f00',
            'carpenter': '#795548',
            'gardener': '#27ae60',
            'pest_control': '#8e44ad',
            'locksmith': '#d35400',
            'tutor': '#2980b9',
            'photographer': '#2c3e50',
            'event_planner': '#e91e63',
            'fitness_trainer': '#00b894',
            'massage_therapist': '#6c5ce7',
            'interior_designer': '#fd79a8',
            'architect': '#fdcb6e'
        }
        
        # Category icons (emoji-based)
        self.category_icons = {
            'plumber': '🔧',
            'electrician': '⚡',
            'landscaper': '🌿',
            'cleaner': '🧹',
            'painter': '🎨',
            'handyman': '🔨',
            'roofer': '🏠',
            'hvac': '❄️',
            'mover': '🚚',
            'carpenter': '🪚',
            'gardener': '🌱',
            'pest_control': '🐜',
            'locksmith': '🔑',
            'tutor': '📚',
            'photographer': '📷',
            'event_planner': '🎉',
            'fitness_trainer': '💪',
            'massage_therapist': '💆',
            'interior_designer': '🎨',
            'architect': '🏗️'
        }
        
    def generate_html_map(self,
                         providers: List[Dict],
                         center_lat: Optional[float] = None,
                         center_lon: Optional[float] = None,
                         zoom: int = 13,
                         title: str = "LASO App - Service Providers",
                         width: int = 1000,
                         height: int = 700,
                         include_controls: bool = True,
                         cluster: bool = False,
                         show_distance: bool = True,
                         user_location: Optional[Tuple[float, float]] = None,
                         dark_mode: bool = False) -> str:
        """
        Generate an HTML map with provider markers.
        
        Args:
            providers: List of provider dictionaries
            center_lat, center_lon: Map center coordinates
            zoom: Initial zoom level
            title: Map title
            width: Map width in pixels
            height: Map height in pixels
            include_controls: Include zoom/pan controls
            cluster: Enable marker clustering
            show_distance: Show distance from user
            user_location: User's location (lat, lon)
            dark_mode: Use dark theme
        
        Returns:
            HTML string for the map
        """
        # Determine center if not provided
        if center_lat is None or center_lon is None:
            if providers and len(providers) > 0:
                # Use average of provider coordinates
                lats = [p.get('latitude', 0) for p in providers if 'latitude' in p]
                lons = [p.get('longitude', 0) for p in providers if 'longitude' in p]
                if lats and lons:
                    center_lat = sum(lats) / len(lats)
                    center_lon = sum(lons) / len(lons)
                else:
                    center_lat, center_lon = 40.7128, -74.0060  # Default NYC
            else:
                center_lat, center_lon = 40.7128, -74.0060
        
        # Prepare provider data for JavaScript
        provider_data = []
        for provider in providers:
            if 'latitude' in provider and 'longitude' in provider:
                lat = provider['latitude']
                lon = provider['longitude']
                
                # Calculate distance if user location provided
                distance = None
                if user_location and show_distance:
                    user_lat, user_lon = user_location
                    if self.location_service:
                        distance = self.location_service.calculate_distance(
                            user_lat, user_lon, lat, lon
                        )
                    else:
                        # Fallback calculation
                        distance = math.sqrt(
                            (lat - user_lat)**2 + (lon - user_lon)**2
                        ) * 111  # Approximate km per degree
                
                data = {
                    'id': provider.get('id', 0),
                    'name': provider.get('name', 'Provider'),
                    'category': provider.get('category', 'Other'),
                    'latitude': lat,
                    'longitude': lon,
                    'rating': provider.get('rating', 0),
                    'address': provider.get('address', ''),
                    'phone': provider.get('phone', ''),
                    'price_range': provider.get('price_range', '$'),
                    'available': provider.get('available', True),
                    'description': provider.get('description', ''),
                    'years_experience': provider.get('years_experience', 0),
                    'total_reviews': provider.get('total_reviews', 0),
                    'website': provider.get('website', ''),
                    'email': provider.get('email', ''),
                    'color': self._get_category_color(provider.get('category', 'Other')),
                    'icon': self._get_category_icon(provider.get('category', 'Other')),
                    'distance': distance if distance is not None else 0,
                    'distance_display': self._format_distance(distance) if distance is not None else ''
                }
                provider_data.append(data)
        
        # Get user location for display
        user_lat = user_location[0] if user_location else center_lat
        user_lon = user_location[1] if user_location else center_lon
        
        # Generate HTML
        html = self._generate_map_html(
            provider_data,
            user_lat,
            user_lon,
            center_lat,
            center_lon,
            zoom,
            title,
            width,
            height,
            include_controls,
            cluster,
            dark_mode
        )
        
        return html
    
    def _generate_map_html(self,
                          providers: List[Dict],
                          user_lat: float,
                          user_lon: float,
                          center_lat: float,
                          center_lon: float,
                          zoom: int,
                          title: str,
                          width: int,
                          height: int,
                          include_controls: bool,
                          cluster: bool,
                          dark_mode: bool) -> str:
        """Generate the actual HTML for the map"""
        
        # Prepare data
        providers_json = json.dumps(providers)
        icons_json = json.dumps(self.category_icons)
        colors_json = json.dumps(self.category_colors)
        
        # Theme settings
        if dark_mode:
            tile_layer = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            tile_attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>, &copy; CartoDB'
            background_color = '#1a1a2e'
            text_color = '#ffffff'
            panel_bg = 'rgba(30, 30, 50, 0.9)'
            panel_text = '#e0e0e0'
            border_color = '#444'
        else:
            tile_layer = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            tile_attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            background_color = '#f0f0f0'
            text_color = '#333333'
            panel_bg = 'rgba(255, 255, 255, 0.95)'
            panel_text = '#333333'
            border_color = '#ccc'
        
        # Generate HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css" />
    {self._get_cluster_script(cluster)}
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            background: {background_color};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            padding: 20px;
        }}
        .map-container {{
            max-width: {width}px;
            margin: 0 auto;
            background: {background_color};
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .map-header {{
            padding: 15px 20px;
            background: {panel_bg};
            border-bottom: 1px solid {border_color};
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }}
        .map-header h2 {{
            color: {text_color};
            font-size: 20px;
            font-weight: 600;
            margin: 0;
        }}
        .map-header .stats {{
            color: {panel_text};
            font-size: 14px;
        }}
        .map-header .stats span {{
            margin-left: 15px;
        }}
        #map {{
            width: 100%;
            height: {height}px;
            background: {background_color};
        }}
        .info-panel {{
            position: absolute;
            bottom: 30px;
            left: 20px;
            background: {panel_bg};
            padding: 12px 18px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            z-index: 1000;
            max-height: 250px;
            overflow-y: auto;
            backdrop-filter: blur(10px);
            border: 1px solid {border_color};
            color: {panel_text};
            font-size: 13px;
            min-width: 150px;
        }}
        .info-panel h4 {{
            margin: 0 0 8px 0;
            color: {text_color};
            font-size: 14px;
            font-weight: 600;
        }}
        .info-panel p {{
            margin: 3px 0;
            font-size: 12px;
            color: {panel_text};
        }}
        .info-panel .stat-item {{
            display: flex;
            justify-content: space-between;
            padding: 2px 0;
        }}
        .info-panel .stat-item .label {{
            opacity: 0.7;
        }}
        .info-panel .stat-item .value {{
            font-weight: 500;
        }}
        .controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: {panel_bg};
            padding: 10px 14px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid {border_color};
            backdrop-filter: blur(10px);
            min-width: 150px;
        }}
        .controls label {{
            color: {panel_text};
            font-size: 12px;
            display: block;
            margin-bottom: 4px;
        }}
        .controls select {{
            width: 100%;
            padding: 6px 10px;
            border: 1px solid {border_color};
            border-radius: 4px;
            background: {background_color};
            color: {text_color};
            font-size: 13px;
            cursor: pointer;
        }}
        .controls select:focus {{
            outline: none;
            border-color: #3498db;
        }}
        .controls .search-input {{
            width: 100%;
            padding: 6px 10px;
            border: 1px solid {border_color};
            border-radius: 4px;
            background: {background_color};
            color: {text_color};
            font-size: 13px;
            margin-top: 6px;
        }}
        .controls .search-input:focus {{
            outline: none;
            border-color: #3498db;
        }}
        .custom-popup .leaflet-popup-content-wrapper {{
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            background: {panel_bg};
            color: {panel_text};
            border: 1px solid {border_color};
            padding: 0;
        }}
        .custom-popup .leaflet-popup-content {{
            padding: 0;
            min-width: 250px;
            max-width: 350px;
        }}
        .custom-popup .leaflet-popup-tip {{
            background: {panel_bg};
        }}
        .custom-popup .popup-content {{
            padding: 15px;
        }}
        .custom-popup .popup-content h3 {{
            margin: 0 0 5px 0;
            color: {text_color};
            font-size: 16px;
            font-weight: 600;
        }}
        .custom-popup .popup-content .category {{
            color: #7f8c8d;
            font-size: 13px;
            display: inline-block;
            background: rgba(0,0,0,0.1);
            padding: 2px 10px;
            border-radius: 12px;
        }}
        .custom-popup .popup-content .rating {{
            color: #f39c12;
            font-weight: bold;
            font-size: 14px;
        }}
        .custom-popup .popup-content .price {{
            color: #27ae60;
            font-weight: 500;
        }}
        .custom-popup .popup-content .distance {{
            color: #3498db;
        }}
        .custom-popup .popup-content .info-item {{
            margin: 4px 0;
            font-size: 12px;
            color: {panel_text};
        }}
        .custom-popup .popup-content .info-item .label {{
            opacity: 0.6;
        }}
        .custom-popup .popup-content .status {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}
        .custom-popup .popup-content .status.available {{
            background: #27ae60;
            color: white;
        }}
        .custom-popup .popup-content .status.unavailable {{
            background: #e74c3c;
            color: white;
        }}
        .custom-popup .popup-content .divider {{
            height: 1px;
            background: {border_color};
            margin: 8px 0;
        }}
        .custom-marker {{
            background: none;
            border: none;
        }}
        .marker-content {{
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
            font-size: 16px;
            transition: transform 0.2s;
        }}
        .marker-content:hover {{
            transform: scale(1.15);
        }}
        .marker-content .rating-badge {{
            position: absolute;
            bottom: -4px;
            right: -4px;
            background: #2c3e50;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid white;
            font-weight: bold;
        }}
        .legend {{
            position: absolute;
            bottom: 30px;
            right: 20px;
            background: {panel_bg};
            padding: 10px 14px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            border: 1px solid {border_color};
            backdrop-filter: blur(10px);
            z-index: 1000;
            max-height: 200px;
            overflow-y: auto;
            color: {panel_text};
        }}
        .legend h5 {{
            margin: 0 0 8px 0;
            color: {text_color};
            font-size: 13px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            margin: 3px 0;
            font-size: 12px;
        }}
        .legend-item .color-box {{
            width: 14px;
            height: 14px;
            border-radius: 50%;
            margin-right: 8px;
            border: 1px solid {border_color};
        }}
        .loading {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: {height}px;
            color: {text_color};
            font-size: 18px;
            background: {background_color};
        }}
        .loading-spinner {{
            border: 3px solid {border_color};
            border-top: 3px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-right: 15px;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        @media (max-width: 768px) {{
            .map-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
            .map-header .stats span {{
                display: block;
                margin-left: 0;
            }}
            .controls {{
                top: 10px;
                right: 10px;
                min-width: 120px;
                padding: 8px 10px;
            }}
            .info-panel {{
                bottom: 10px;
                left: 10px;
                padding: 8px 12px;
                min-width: 120px;
            }}
            .legend {{
                bottom: 10px;
                right: 10px;
                padding: 8px 10px;
            }}
            .custom-popup .leaflet-popup-content {{
                min-width: 200px;
            }}
        }}
    </style>
</head>
<body>
    <div class="map-container">
        <div class="map-header">
            <h2>📍 {title}</h2>
            <div class="stats">
                <span>📊 <span id="providerCount">{len(providers)}</span> providers</span>
                <span>📂 <span id="categoryCount">0</span> categories</span>
                <span id="userLocationDisplay" style="display:none;">📍 <span id="userLocationText"></span></span>
            </div>
        </div>
        <div id="map">
            <div class="loading" id="loading">
                <div class="loading-spinner"></div>
                <span>Loading map...</span>
            </div>
        </div>
    </div>
    
    <script>
        // Data
        const providers = {providers_json};
        const categoryIcons = {icons_json};
        const categoryColors = {colors_json};
        
        // User location
        const userLat = {user_lat};
        const userLon = {user_lon};
        
        // Configuration
        const showDistance = {str(show_distance).lower()};
        const darkMode = {str(dark_mode).lower()};
        
        // Initialize map
        const map = L.map('map', {{
            center: [{center_lat}, {center_lon}],
            zoom: {zoom},
            zoomControl: {str(include_controls).lower()},
            fadeAnimation: true,
            zoomAnimation: true,
            attributionControl: true
        }});
        
        // Add tile layer
        L.tileLayer('{tile_layer}', {{
            attribution: '{tile_attribution}',
            maxZoom: 19,
            minZoom: 3
        }}).addTo(map);
        
        // Hide loading
        document.getElementById('loading').style.display = 'none';
        
        // Create marker icons
        function getMarkerIcon(category, available, rating) {{
            const color = categoryColors[category.toLowerCase()] || '#78909c';
            const opacity = available ? 1 : 0.5;
            const icon = categoryIcons[category.toLowerCase()] || '📍';
            
            return L.divIcon({{
                html: `
                    <div class="marker-content" style="background-color:{color};opacity:{opacity};position:relative;">
                        ${{icon}}
                        <div class="rating-badge">${{Math.round(rating)}}</div>
                    </div>
                `,
                className: 'custom-marker',
                iconSize: [36, 36],
                iconAnchor: [18, 18],
                popupAnchor: [0, -18]
            }});
        }}
        
        // Create popup content
        function createPopupContent(provider) {{
            const rating = provider.rating || 0;
            const fullStars = Math.floor(rating);
            const halfStar = rating - fullStars >= 0.5;
            let stars = '★'.repeat(fullStars);
            if (halfStar) stars += '½';
            stars += '☆'.repeat(5 - fullStars - (halfStar ? 1 : 0));
            
            const availableText = provider.available ? 
                '<span class="status available">✅ Available</span>' : 
                '<span class="status unavailable">❌ Unavailable</span>';
            
            const distanceText = provider.distance ? 
                `<div class="info-item distance">📏 ${provider.distance_display | provider.distance.toFixed(2) + ' km'}</div>` : '';
            
            return `
                <div class="popup-content">
                    <h3>${{provider.name}}</h3>
                    <div class="category">${{provider.category}} ${{categoryIcons[provider.category.toLowerCase()] || ''}}</div>
                    <div class="rating">${{stars}} (${{rating.toFixed(1)}})</div>
                    <div class="price">${{provider.price_range || '$'}}</div>
                    <div class="info-item">${{availableText}}</div>
                    ${{provider.address ? `<div class="info-item">📍 ${{provider.address}}</div>` : ''}}
                    ${{provider.phone ? `<div class="info-item">📞 ${{provider.phone}}</div>` : ''}}
                    ${{provider.email ? `<div class="info-item">✉️ ${{provider.email}}</div>` : ''}}
                    ${{provider.website ? `<div class="info-item">🌐 <a href="http://${{provider.website}}" target="_blank">${{provider.website}}</a></div>` : ''}}
                    ${{provider.years_experience ? `<div class="info-item">💼 ${{provider.years_experience}} years experience</div>` : ''}}
                    ${{provider.total_reviews ? `<div class="info-item">📝 ${{provider.total_reviews}} reviews</div>` : ''}}
                    ${{provider.description ? `<div class="divider"></div><div class="info-item">${{provider.description}}</div>` : ''}}
                    ${{distanceText}}
                </div>
            `;
        }}
        
        // Add markers
        const markers = [];
        const categories = new Set();
        
        providers.forEach(provider => {{
            categories.add(provider.category);
            
            const icon = getMarkerIcon(provider.category, provider.available, provider.rating);
            const marker = L.marker([provider.latitude, provider.longitude], {{
                icon: icon
            }});
            
            marker.bindPopup(createPopupContent(provider), {{
                className: 'custom-popup',
                maxWidth: 350,
                minWidth: 250
            }});
            
            marker.on('mouseover', function(e) {{
                this.openPopup();
            }});
            
            marker.on('mouseout', function(e) {{
                this.closePopup();
            }});
            
            marker.addTo(map);
            markers.push(marker);
        }});
        
        // Add marker clustering if enabled
        {self._get_cluster_code(cluster)}
        
        // Add user location marker
        L.circleMarker([userLat, userLon], {{
            radius: 8,
            fillColor: '#e74c3c',
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        }}).addTo(map).bindPopup('📍 Your Location');
        
        L.circle([userLat, userLon], {{
            radius: 100,
            color: '#e74c3c',
            weight: 1,
            opacity: 0.3,
            fillColor: '#e74c3c',
            fillOpacity: 0.05
        }}).addTo(map);
        
        // Update stats
        document.getElementById('categoryCount').textContent = categories.size;
        
        // Add controls if requested
        {self._get_controls_code(include_controls)}
        
        // Add info panel
        const infoPanel = L.control({{ position: 'bottomleft' }});
        infoPanel.onAdd = function() {{
            const div = L.DomUtil.create('div', 'info-panel');
            const categoryList = Array.from(categories).join(', ');
            div.innerHTML = `
                <h4>📍 Service Providers</h4>
                <div class="stat-item">
                    <span class="label">Total:</span>
                    <span class="value">${{providers.length}}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Categories:</span>
                    <span class="value">${{categories.size}}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Available:</span>
                    <span class="value">${{providers.filter(p => p.available).length}}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Avg Rating:</span>
                    <span class="value">${{(providers.reduce((sum, p) => sum + p.rating, 0) / providers.length).toFixed(1)}}</span>
                </div>
                <p style="margin-top:8px;font-size:11px;opacity:0.6;">Categories: ${{categoryList.substring(0, 50)}}${{categoryList.length > 50 ? '...' : ''}}</p>
            `;
            return div;
        }};
        infoPanel.addTo(map);
        
        // Add legend
        const legend = L.control({{ position: 'bottomright' }});
        legend.onAdd = function() {{
            const div = L.DomUtil.create('div', 'legend');
            const items = Array.from(categories).slice(0, 8);
            div.innerHTML = `
                <h5>📌 Categories</h5>
                ${{items.map(cat => `
                    <div class="legend-item">
                        <div class="color-box" style="background-color:${{categoryColors[cat.toLowerCase()] || '#78909c'}};"></div>
                        <span>${{cat}} ${{categoryIcons[cat.toLowerCase()] || ''}}</span>
                    </div>
                `).join('')}}
                ${{categories.size > 8 ? `<div class="legend-item" style="opacity:0.6;">+${categories.size - 8} more</div>` : ''}}
            `;
            return div;
        }};
        legend.addTo(map);
        
        // Fit bounds to show all markers
        if (providers.length > 0) {{
            const bounds = L.latLngBounds(providers.map(p => [p.latitude, p.longitude]));
            bounds.extend([userLat, userLon]);
            map.fitBounds(bounds, {{ padding: [50, 50] }});
        }}
        
        // Handle window resize
        window.addEventListener('resize', function() {{
            map.invalidateSize();
        }});
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'r' || e.key === 'R') {{
                map.setView([{center_lat}, {center_lon}], {zoom});
            }}
        }});
    </script>
</body>
</html>'''
        
        return html
    
    def _get_cluster_script(self, cluster: bool) -> str:
        """Get cluster plugin script if needed"""
        if not cluster:
            return ''
        return '''
        <script src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"></script>
        '''
    
    def _get_cluster_code(self, cluster: bool) -> str:
        """Get clustering code if enabled"""
        if not cluster:
            return '''
        // Clustering disabled
        const markerCluster = null;
        '''
        return '''
        // Add marker clustering
        const markerClusterGroup = L.markerClusterGroup({
            maxClusterRadius: 80,
            iconCreateFunction: function(cluster) {
                const childCount = cluster.getChildCount();
                const markers = cluster.getAllChildMarkers();
                let avgRating = 0;
                markers.forEach(m => {
                    const popup = m.getPopup();
                    if (popup) {
                        const content = popup.getContent();
                        const ratingMatch = content.match(/★.*?\((\\d+\\.?\\d*)\)/);
                        if (ratingMatch) {
                            avgRating += parseFloat(ratingMatch[1]);
                        }
                    }
                });
                avgRating = avgRating / markers.length;
                
                const size = childCount < 10 ? 'small' : childCount < 100 ? 'medium' : 'large';
                const colors = {
                    small: '#3498db',
                    medium: '#f39c12',
                    large: '#e74c3c'
                };
                const color = childCount < 10 ? '#3498db' : childCount < 100 ? '#f39c12' : '#e74c3c';
                
                return L.divIcon({
                    html: `<div style="background-color:${color};color:white;border-radius:50%;width:${childCount < 10 ? 30 : childCount < 100 ? 40 : 50}px;height:${childCount < 10 ? 30 : childCount < 100 ? 40 : 50}px;display:flex;align-items:center;justify-content:center;font-weight:bold;border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.3);font-size:${childCount < 10 ? 12 : 14}px;">
                        ${childCount}
                        ${avgRating > 0 ? `<span style="font-size:9px;margin-left:2px;">★${avgRating.toFixed(1)}</span>` : ''}
                    </div>`,
                    className: 'marker-cluster',
                    iconSize: [childCount < 10 ? 30 : childCount < 100 ? 40 : 50, childCount < 10 ? 30 : childCount < 100 ? 40 : 50],
                    iconAnchor: [childCount < 10 ? 15 : childCount < 100 ? 20 : 25, childCount < 10 ? 15 : childCount < 100 ? 20 : 25]
                });
            }
        });
        
        markers.forEach(marker => markerClusterGroup.addLayer(marker));
        map.addLayer(markerClusterGroup);
        
        // Store for filtering
        const markerClusterGroupRef = markerClusterGroup;
        '''
    
    def _get_controls_code(self, include_controls: bool) -> str:
        """Get control code if enabled"""
        if not include_controls:
            return '''
        // Controls disabled
        '''
        return '''
        // Add search and filter controls
        const controlDiv = document.createElement('div');
        controlDiv.className = 'controls';
        controlDiv.innerHTML = `
            <label for="categoryFilter">Filter by Category:</label>
            <select id="categoryFilter" onchange="filterByCategory(this.value)">
                <option value="">All Categories</option>
                ${Array.from(categories).map(c => 
                    `<option value="${c}">${c} ${categoryIcons[c.toLowerCase()] || ''}</option>`
                ).join('')}
            </select>
            <input type="text" class="search-input" id="searchInput" placeholder="🔍 Search providers..." oninput="searchProviders(this.value)" />
        `;
        document.getElementById('map').appendChild(controlDiv);
        
        // Filter functions
        function filterByCategory(category) {
            const searchText = document.getElementById('searchInput').value.toLowerCase();
            const markerGroup = markerCluster || map;
            
            markers.forEach(marker => {
                const provider = providers.find(p => 
                    Math.abs(p.latitude - marker.getLatLng().lat) < 0.0001 && 
                    Math.abs(p.longitude - marker.getLatLng().lng) < 0.0001
                );
                if (provider) {
                    const matchesCategory = category === '' || provider.category === category;
                    const matchesSearch = searchText === '' || 
                        provider.name.toLowerCase().includes(searchText) ||
                        provider.category.toLowerCase().includes(searchText) ||
                        (provider.description && provider.description.toLowerCase().includes(searchText));
                    
                    if (matchesCategory && matchesSearch) {
                        if (markerCluster) {
                            markerClusterGroupRef.addLayer(marker);
                        } else {
                            map.addLayer(marker);
                        }
                    } else {
                        if (markerCluster) {
                            markerClusterGroupRef.removeLayer(marker);
                        } else {
                            map.removeLayer(marker);
                        }
                    }
                }
            });
        }
        
        function searchProviders(query) {
            const category = document.getElementById('categoryFilter').value;
            filterByCategory(category);
        }
        
        // Expose functions globally
        window.filterByCategory = filterByCategory;
        window.searchProviders = searchProviders;
        '''
    
    def _get_category_color(self, category: str) -> str:
        """Get color for a category"""
        return self.category_colors.get(category.lower(), '#78909c')
    
    def _get_category_icon(self, category: str) -> str:
        """Get icon for a category"""
        return self.category_icons.get(category.lower(), '📍')
    
    def _format_distance(self, distance: float) -> str:
        """Format distance for display"""
        if distance is None:
            return ''
        if distance < 1:
            meters = distance * 1000
            return f"{meters:.0f} m"
        else:
            return f"{distance:.2f} km"
    
    def save_map_to_file(self, html: str, filename: str = "service_providers_map.html") -> str:
        """
        Save HTML map to a file.
        
        Args:
            html: HTML string
            filename: Output filename
        
        Returns:
            Path to saved file
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename) if os.path.dirname(filename) else '.', exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return os.path.abspath(filename)
    
    def show_map(self, html: str, open_browser: bool = True) -> str:
        """
        Display the map in a web browser.
        
        Args:
            html: HTML string to display
            open_browser: Whether to open in browser
        
        Returns:
            Path to temporary file
        """
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html)
            temp_path = f.name
        
        # Open in browser
        if open_browser:
            webbrowser.open('file://' + temp_path)
        
        return temp_path
    
    def generate_provider_heatmap(self,
                                 providers: List[Dict],
                                 center_lat: Optional[float] = None,
                                 center_lon: Optional[float] = None,
                                 zoom: int = 12,
                                 radius: int = 25,
                                 blur: int = 15,
                                 dark_mode: bool = False) -> str:
        """
        Generate a heatmap of provider density.
        
        Args:
            providers: List of provider dictionaries
            center_lat, center_lon: Map center
            zoom: Initial zoom level
            radius: Heat radius
            blur: Blur amount
            dark_mode: Use dark theme
        
        Returns:
            HTML string for heatmap
        """
        # Get coordinates for heatmap
        points = []
        for provider in providers:
            if 'latitude' in provider and 'longitude' in provider:
                points.append({
                    'lat': provider['latitude'],
                    'lon': provider['longitude'],
                    'weight': provider.get('rating', 1) / 5  # Normalize rating to 0-1
                })
        
        points_json = json.dumps(points)
        
        # Determine center if not provided
        if center_lat is None or center_lon is None:
            if points:
                lats = [p['lat'] for p in points]
                lons = [p['lon'] for p in points]
                center_lat = sum(lats) / len(lats)
                center_lon = sum(lons) / len(lons)
            else:
                center_lat, center_lon = 40.7128, -74.0060
        
        # Theme
        bg_color = '#1a1a2e' if dark_mode else '#f0f0f0'
        text_color = '#ffffff' if dark_mode else '#333333'
        tile_layer = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" if dark_mode else "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        tile_attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' + (', &copy; CartoDB' if dark_mode else '')
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>Provider Density Heatmap</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <script src="https://unpkg.com/leaflet-heat@0.2.0/dist/leaflet-heat.js"></script>
    <style>
        body {{ margin: 0; padding: 0; background: {bg_color}; }}
        #map {{ width: 100%; height: 100vh; }}
        .heatmap-header {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.7);
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-family: Arial, sans-serif;
        }}
        .heatmap-header h2 {{
            margin: 0;
            font-size: 18px;
        }}
        .heatmap-header p {{
            margin: 5px 0 0 0;
            font-size: 13px;
            opacity: 0.8;
        }}
        .stats {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.7);
            padding: 10px 16px;
            border-radius: 8px;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 13px;
        }}
        .stats span {{
            margin-right: 15px;
        }}
    </style>
</head>
<body>
    <div id="map">
        <div class="heatmap-header">
            <h2>🔥 Provider Density Heatmap</h2>
            <p>Showing {len(points)} providers</p>
        </div>
        <div class="stats">
            <span>📊 Total: {len(points)}</span>
            <span>⭐ Avg Rating: {(sum(p['weight'] for p in points) / len(points) * 5) if points else 0:.1f}</span>
        </div>
    </div>
    <script>
        const points = {points_json};
        
        const map = L.map('map').setView([{center_lat}, {center_lon}], {zoom});
        
        L.tileLayer('{tile_layer}', {{
            attribution: '{tile_attribution}',
            maxZoom: 19
        }}).addTo(map);
        
        // Create heatmap layer
        const heat = L.heatLayer(
            points.map(p => [p.lat, p.lon, p.weight || 0.5]),
            {{
                radius: {radius},
                blur: {blur},
                maxZoom: 17,
                gradient: {{
                    0.0: 'blue',
                    0.2: 'cyan',
                    0.4: 'lime',
                    0.6: 'yellow',
                    0.8: 'orange',
                    1.0: 'red'
                }}
            }}
        ).addTo(map);
        
        // Fit bounds to show all points
        if (points.length > 0) {{
            const bounds = L.latLngBounds(points.map(p => [p.lat, p.lon]));
            map.fitBounds(bounds, {{ padding: [50, 50] }});
        }}
    </script>
</body>
</html>'''
        
        return html
    
    def generate_route_map(self,
                          start_lat: float,
                          start_lon: float,
                          end_lat: float,
                          end_lon: float,
                          providers: Optional[List[Dict]] = None,
                          title: str = "Route Map",
                          dark_mode: bool = False) -> str:
        """
        Generate a map showing route between two points.
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            providers: List of providers to show along route
            title: Map title
            dark_mode: Use dark theme
        
        Returns:
            HTML string for route map
        """
        providers_json = json.dumps(providers or [])
        
        # Theme
        bg_color = '#1a1a2e' if dark_mode else '#f0f0f0'
        tile_layer = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" if dark_mode else "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        tile_attribution = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' + (', &copy; CartoDB' if dark_mode else '')
        
        # Calculate midpoint and distance
        mid_lat = (start_lat + end_lat) / 2
        mid_lon = (start_lon + end_lon) / 2
        if self.location_service:
            distance = self.location_service.calculate_distance(start_lat, start_lon, end_lat, end_lon)
        else:
            distance = math.sqrt((end_lat - start_lat)**2 + (end_lon - start_lon)**2) * 111
        
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; background: {bg_color}; }}
        #map {{ width: 100%; height: 100vh; }}
        .route-header {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 1000;
            background: rgba(0,0,0,0.7);
            padding: 12px 20px;
            border-radius: 8px;
            color: white;
            font-family: Arial, sans-serif;
        }}
        .route-header h2 {{
            margin: 0;
            font-size: 18px;
        }}
        .route-header p {{
            margin: 5px 0 0 0;
            font-size: 13px;
            opacity: 0.8;
        }}
        .route-info {{
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 1000;
            background: rgba(0,0,0,0.7);
            padding: 10px 20px;
            border-radius: 8px;
            color: white;
            font-family: Arial, sans-serif;
            font-size: 14px;
            text-align: center;
        }}
        .route-info span {{
            margin: 0 10px;
        }}
    </style>
</head>
<body>
    <div id="map">
        <div class="route-header">
            <h2>🗺️ {title}</h2>
            <p>Distance: {distance:.2f} km</p>
        </div>
        <div class="route-info">
            <span>🏁 Start</span>
            <span>➡️ {distance:.2f} km</span>
            <span>🎯 Destination</span>
        </div>
    </div>
    <script>
        const start = [{start_lat}, {start_lon}];
        const end = [{end_lat}, {end_lon}];
        const providers = {providers_json};
        
        const map = L.map('map').setView([{mid_lat}, {mid_lon}], 12);
        
        L.tileLayer('{tile_layer}', {{
            attribution: '{tile_attribution}',
            maxZoom: 19
        }}).addTo(map);
        
        // Start marker
        L.marker(start, {{
            icon: L.divIcon({{
                html: '🏁',
                className: 'custom-marker',
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            }})
        }}).addTo(map).bindPopup('📍 Start');
        
        // End marker
        L.marker(end, {{
            icon: L.divIcon({{
                html: '🎯',
                className: 'custom-marker',
                iconSize: [32, 32],
                iconAnchor: [16, 16]
            }})
        }}).addTo(map).bindPopup('📍 Destination');
        
        // Draw route line
        L.polyline([start, end], {{
            color: '#3498db',
            weight: 4,
            opacity: 0.8,
            dashArray: '10, 10'
        }}).addTo(map).bindPopup('Route');
        
        // Add provider markers along route
        providers.forEach(p => {{
            if (p.latitude && p.longitude) {{
                L.circleMarker([p.latitude, p.longitude], {{
                    radius: 7,
                    fillColor: '#e74c3c',
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.8
                }}).addTo(map).bindPopup(`${{p.name || 'Provider'}}`);
            }}
        }});
        
        // Fit bounds with padding
        const bounds = L.latLngBounds([start, end]);
        map.fitBounds(bounds, {{ padding: [80, 80] }});
    </script>
</body>
</html>'''
        
        return html
    
    def create_provider_map(self, 
                           providers: List[Dict], 
                           show_browser: bool = True,
                           filename: Optional[str] = None,
                           **kwargs) -> str:
        """
        Create and optionally display a provider map.
        
        Args:
            providers: List of providers
            show_browser: Whether to open in browser
            filename: Output filename (optional)
            **kwargs: Additional arguments for generate_html_map
        
        Returns:
            Path to the generated HTML file
        """
        html = self.generate_html_map(providers, **kwargs)
        
        if filename:
            filepath = self.save_map_to_file(html, filename)
        else:
            filepath = self.save_map_to_file(html)
        
        if show_browser:
            webbrowser.open('file://' + filepath)
        
        return filepath
    
    def create_heatmap(self, 
                      providers: List[Dict],
                      show_browser: bool = True,
                      filename: Optional[str] = None,
                      **kwargs) -> str:
        """
        Create and display a heatmap.
        
        Args:
            providers: List of providers
            show_browser: Whether to open in browser
            filename: Output filename (optional)
            **kwargs: Additional arguments for generate_provider_heatmap
        
        Returns:
            Path to the generated HTML file
        """
        html = self.generate_provider_heatmap(providers, **kwargs)
        
        if filename:
            filepath = self.save_map_to_file(html, filename)
        else:
            filepath = self.save_map_to_file(html, "heatmap.html")
        
        if show_browser:
            webbrowser.open('file://' + filepath)
        
        return filepath
    
    def create_route_map(self,
                        start_lat: float,
                        start_lon: float,
                        end_lat: float,
                        end_lon: float,
                        providers: Optional[List[Dict]] = None,
                        show_browser: bool = True,
                        filename: Optional[str] = None,
                        **kwargs) -> str:
        """
        Create and display a route map.
        
        Args:
            start_lat, start_lon: Starting coordinates
            end_lat, end_lon: Ending coordinates
            providers: Providers to show
            show_browser: Whether to open in browser
            filename: Output filename (optional)
            **kwargs: Additional arguments for generate_route_map
        
        Returns:
            Path to the generated HTML file
        """
        html = self.generate_route_map(start_lat, start_lon, end_lat, end_lon, providers, **kwargs)
        
        if filename:
            filepath = self.save_map_to_file(html, filename)
        else:
            filepath = self.save_map_to_file(html, "route_map.html")
        
        if show_browser:
            webbrowser.open('file://' + filepath)
        
        return filepath
    
    def create_compare_map(self,
                          providers: List[Dict],
                          compare_providers: List[Dict],
                          show_browser: bool = True) -> str:
        """
        Create a map comparing two sets of providers.
        
        Args:
            providers: Primary providers
            compare_providers: Comparison providers
            show_browser: Whether to open in browser
        
        Returns:
            Path to the generated HTML file
        """
        # Combine with different colors
        for p in providers:
            p['_color'] = '#3498db'  # Blue for primary
            p['_group'] = 'Primary'
        
        for p in compare_providers:
            p['_color'] = '#e74c3c'  # Red for comparison
            p['_group'] = 'Comparison'
        
        all_providers = providers + compare_providers
        
        html = self.generate_html_map(all_providers, title="Provider Comparison")
        filepath = self.save_map_to_file(html, "compare_map.html")
        
        if show_browser:
            webbrowser.open('file://' + filepath)
        
        return filepath
    
    def get_map_url(self, 
                   providers: List[Dict],
                   center_lat: Optional[float] = None,
                   center_lon: Optional[float] = None,
                   zoom: int = 13) -> str:
        """
        Generate a URL for an online map service.
        
        Args:
            providers: List of providers
            center_lat, center_lon: Map center
            zoom: Zoom level
        
        Returns:
            URL string
        """
        # Use OpenStreetMap or Google Maps
        base_url = "https://www.openstreetmap.org/"
        
        if center_lat is None or center_lon is None:
            if providers:
                lats = [p.get('latitude', 0) for p in providers if 'latitude' in p]
                lons = [p.get('longitude', 0) for p in providers if 'longitude' in p]
                if lats and lons:
                    center_lat = sum(lats) / len(lats)
                    center_lon = sum(lons) / len(lons)
                else:
                    center_lat, center_lon = 40.7128, -74.0060
            else:
                center_lat, center_lon = 40.7128, -74.0060
        
        # Build query parameters
        params = {
            'mlat': center_lat,
            'mlon': center_lon,
            'zoom': zoom
        }
        
        # Add markers for each provider
        marker_params = []
        for i, provider in enumerate(providers):
            if 'latitude' in provider and 'longitude' in provider:
                marker_params.append(f"mlat{i+1}={provider['latitude']}&mlon{i+1}={provider['longitude']}")
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()] + marker_params)
        
        return f"{base_url}?{query_string}"
    
    def generate_static_map_image(self,
                                 providers: List[Dict],
                                 width: int = 600,
                                 height: int = 400,
                                 zoom: int = 13) -> bytes:
        """
        Generate a static map image (requires external service).
        
        This is a placeholder - in production, use:
        - Google Static Maps API
        - Mapbox Static API
        - OpenStreetMap static maps
        
        Args:
            providers: List of providers
            width: Image width
            height: Image height
            zoom: Zoom level
        
        Returns:
            Image bytes
        """
        # This would require an external service
        # For now, return a placeholder message
        raise NotImplementedError("Static map generation requires external service")
    
    def get_map_statistics(self, providers: List[Dict]) -> Dict[str, Any]:
        """
        Get statistics about providers for map display.
        
        Args:
            providers: List of providers
        
        Returns:
            Statistics dictionary
        """
        if not providers:
            return {
                'total': 0,
                'categories': [],
                'avg_rating': 0,
                'available': 0,
                'unavailable': 0,
                'price_ranges': {},
                'bounds': None
            }
        
        categories = set()
        total_rating = 0
        available_count = 0
        price_ranges = {}
        lats = []
        lons = []
        
        for provider in providers:
            category = provider.get('category', 'Other')
            categories.add(category)
            
            rating = provider.get('rating', 0)
            total_rating += rating
            
            if provider.get('available', True):
                available_count += 1
            
            price = provider.get('price_range', '$')
            price_ranges[price] = price_ranges.get(price, 0) + 1
            
            if 'latitude' in provider:
                lats.append(provider['latitude'])
            if 'longitude' in provider:
                lons.append(provider['longitude'])
        
        return {
            'total': len(providers),
            'categories': list(categories),
            'avg_rating': total_rating / len(providers) if providers else 0,
            'available': available_count,
            'unavailable': len(providers) - available_count,
            'price_ranges': price_ranges,
            'bounds': {
                'min_lat': min(lats) if lats else None,
                'max_lat': max(lats) if lats else None,
                'min_lon': min(lons) if lons else None,
                'max_lon': max(lons) if lons else None
            }
        }


if __name__ == "__main__":
    # Test map integration
    from location_service import LocationService
    
    print("=" * 70)
    print("🗺️ Map Integration Test")
    print("=" * 70)
    
    # Get service and providers
    service = LocationService()
    providers = service.get_mock_providers()
    
    print(f"\n📋 Loaded {len(providers)} providers")
    
    # Create map integration
    map_integration = MapIntegration(service)
    
    # Test 1: Provider Map
    print("\n📍 Test 1: Generating Provider Map")
    print("-" * 40)
    filepath = map_integration.create_provider_map(
        providers, 
        show_browser=False,
        title="LASO App - Service Providers Map",
        cluster=True,
        user_location=(40.7128, -74.0060)
    )
    print(f"✅ Map saved to: {filepath}")
    
    # Test 2: Heatmap
    print("\n🔥 Test 2: Generating Heatmap")
    print("-" * 40)
    heatmap_path = map_integration.create_heatmap(
        providers,
        show_browser=False,
        radius=30,
        blur=20
    )
    print(f"✅ Heatmap saved to: {heatmap_path}")
    
    # Test 3: Route Map
    print("\n🗺️ Test 3: Generating Route Map")
    print("-" * 40)
    route_path = map_integration.create_route_map(
        40.7128, -74.0060,  # Start (NYC)
        40.7589, -73.9851,  # End (Midtown)
        providers[:5],
        show_browser=False,
        title="Route to Provider"
    )
    print(f"✅ Route map saved to: {route_path}")
    
    # Test 4: Statistics
    print("\n📊 Test 4: Map Statistics")
    print("-" * 40)
    stats = map_integration.get_map_statistics(providers)
    print(f"  Total: {stats['total']}")
    print(f"  Categories: {', '.join(stats['categories'][:5])}...")
    print(f"  Avg Rating: {stats['avg_rating']:.1f}")
    print(f"  Available: {stats['available']}/{stats['total']}")
    
    # Test 5: Open in browser
    print("\n🌐 Opening maps in browser...")
    webbrowser.open('file://' + filepath)
    
    print("\n" + "=" * 70)
    print("✅ Map integration test complete!")
    print("=" * 70)
    print("\n📁 Generated files:")
    print(f"  - {filepath}")
    print(f"  - {heatmap_path}")
    print(f"  - {route_path}")