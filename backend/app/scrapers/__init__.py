"""Scraping module"""
from .tor_client import tor_client, TorClient
from .base_scraper import BaseScraper
from .paste_scraper import PasteScraper

__all__ = ["tor_client", "TorClient", "BaseScraper", "PasteScraper"]
