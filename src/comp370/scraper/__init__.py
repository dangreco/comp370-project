"""
Web scraper for extracting Seinfeld episode data from IMSDB.

This module provides functionality to scrape Seinfeld scripts, episode metadata,
and season information from the Internet Movie Script Database.
"""

from .client import Client

__all__ = ["Client"]
