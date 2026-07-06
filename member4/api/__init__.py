"""
__init__.py - Makes API a package
"""

from .api__endpoints import app

__all__ = ['app']

print("✅ API package initialized")