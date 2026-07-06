"""
Setup script for Location Module
Member 3: Location & Search Module Developer
LASO App - Group 10
"""

from setuptools import setup, find_packages

setup(
    name="laso-location",
    version="1.0.0",
    description="Location and Search Module for LASO App",
    author="Member 3",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "geopy>=2.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "coverage>=6.0.0",
            "black>=21.0.0",
            "flake8>=4.0.0",
            "mypy>=0.910",
        ],
        "map": [
            "folium>=0.14.0",
            "numpy>=1.21.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)