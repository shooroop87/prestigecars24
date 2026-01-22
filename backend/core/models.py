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
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
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