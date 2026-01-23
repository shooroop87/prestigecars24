from django.contrib import admin
from .models import CarCategory, Car, CodeSnippet


@admin.register(CarCategory)
class CarCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price_per_day', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


# Добавить в backend/core/admin.py

@admin.register(CodeSnippet)
class CodeSnippetAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'snippet_type', 'is_active', 'priority', 'updated_at']
    list_filter = ['is_active', 'location', 'snippet_type']
    list_editable = ['is_active', 'priority']
    search_fields = ['name', 'code', 'notes']
    ordering = ['location', 'priority']
    
    fieldsets = (
        ('Basic', {
            'fields': ('name', 'is_active', 'priority')
        }),
        ('Code', {
            'fields': ('snippet_type', 'location', 'code'),
        }),
        ('Conditions', {
            'fields': ('show_on_all_pages', 'show_on_urls', 'exclude_urls'),
            'classes': ('collapse',),
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )
    
    class Media:
        css = {
            'all': ('admin/css/snippets.css',)
        }