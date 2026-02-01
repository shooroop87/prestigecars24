from django.db import models
from django.db import models
from django.utils.text import slugify


class CarCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name = "Car Category"
        verbose_name_plural = "Car Categories"
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Car(models.Model):
    category = models.ForeignKey(CarCategory, on_delete=models.CASCADE, related_name='cars')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Images
    main_image = models.URLField(max_length=500)
    image_2 = models.URLField(max_length=500, blank=True)
    image_3 = models.URLField(max_length=500, blank=True)
    image_4 = models.URLField(max_length=500, blank=True)
    
    # Specs
    seats = models.PositiveIntegerField(default=2)
    transmission = models.CharField(max_length=50, default='Automatic')
    
    # Tags (comma separated)
    tags = models.CharField(max_length=500, blank=True, help_text="Comma separated: Exclusive, Hybrid, Sport")
    
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/{self.category.slug}/{self.slug}/"
    
    def get_tags_list(self):
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_images(self):
        images = [self.main_image]
        for img in [self.image_2, self.image_3, self.image_4]:
            if img:
                images.append(img)
        return images
    

class CodeSnippet(models.Model):
    """Система code snippets как WPCode для header/footer скриптов"""
    
    class Location(models.TextChoices):
        HEAD_START = 'head_start', 'Head - Start'
        HEAD_END = 'head_end', 'Head - End'
        BODY_START = 'body_start', 'Body - Start (after <body>)'
        BODY_END = 'body_end', 'Body - End (before </body>)'
        FOOTER = 'footer', 'Footer Section'
    
    class SnippetType(models.TextChoices):
        HTML = 'html', 'HTML'
        JS = 'js', 'JavaScript'
        CSS = 'css', 'CSS'
        
    name = models.CharField(max_length=200, help_text="GTM, Google Ads, Meta Pixel, etc.")
    code = models.TextField(help_text="Paste your code here")
    location = models.CharField(max_length=20, choices=Location.choices, default=Location.HEAD_END)
    snippet_type = models.CharField(max_length=10, choices=SnippetType.choices, default=SnippetType.HTML)
    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=10, help_text="Lower = loads first")
    
    # Условия показа
    show_on_all_pages = models.BooleanField(default=True)
    show_on_urls = models.TextField(blank=True, help_text="One URL per line, e.g. /contacts/")
    exclude_urls = models.TextField(blank=True, help_text="Exclude these URLs")
    
    # Мета
    notes = models.TextField(blank=True, help_text="Internal notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['location', 'priority', 'name']
        verbose_name = "Code Snippet"
        verbose_name_plural = "Code Snippets"
    
    def __str__(self):
        status = "✓" if self.is_active else "✗"
        return f"{status} {self.name} ({self.get_location_display()})"
    
    def should_show_on_path(self, path):
        """Проверяет, нужно ли показывать snippet на данном URL"""
        if not self.is_active:
            return False
            
        # Проверяем исключения
        if self.exclude_urls:
            for url in self.exclude_urls.strip().split('\n'):
                if url.strip() and url.strip() in path:
                    return False
        
        # Если показывать везде
        if self.show_on_all_pages:
            return True
        
        # Проверяем конкретные URL
        if self.show_on_urls:
            for url in self.show_on_urls.strip().split('\n'):
                if url.strip() and url.strip() in path:
                    return True
        
        return False
