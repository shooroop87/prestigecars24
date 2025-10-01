# backend/core/sitemaps.py

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap для статических страниц сайта"""
    
    priority = 0.8
    changefreq = "weekly"
    
    def items(self):
        return [
            "core:home"
        ]
    
    def location(self, item):
        return reverse(item)