"""
Forex Trading Analysis Module

This module provides comprehensive forex trading analysis capabilities including:
- Real-time and historical forex data fetching
- Technical analysis for currency pairs
- Risk management tools
- Report generation
"""

from .forex_client import ForexClient
from .forex_manager import ForexManager
from .forex_analyzer import ForexAnalyzer
from .currency_pairs import MAJOR_PAIRS, MINOR_PAIRS, EXOTIC_PAIRS

__version__ = "1.0.0"
__author__ = "Financial Analytics Team"

__all__ = [
    'ForexClient',
    'ForexManager', 
    'ForexAnalyzer',
    'MAJOR_PAIRS',
    'MINOR_PAIRS',
    'EXOTIC_PAIRS'
]
