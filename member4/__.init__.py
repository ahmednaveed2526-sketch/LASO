"""
__init__.py - Makes member4 a Python package
"""

from .user_management import UserManagement
from .communication import Communication

__all__ = ['UserManagement', 'Communication']

print("✅ Member 4 package initialized")