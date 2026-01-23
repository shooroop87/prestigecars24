from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticSitemap(Sitemap):
    """Sitemap для статических страниц"""
    
    protocol = "https"
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return [
            ("index", 1.0, "weekly"),
            ("contacts", 0.8, "monthly"),
            ("faq", 0.7, "monthly"),
            ("privacy", 0.3, "yearly"),
            ("cookies", 0.3, "yearly"),
        ]

    def location(self, item):
        return reverse(item[0])

    def priority(self, item):
        return item[1]

    def changefreq(self, item):
        return item[2]