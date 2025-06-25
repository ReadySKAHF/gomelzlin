from django.contrib import admin
from .models import Category, Product, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'sort_order', 'is_featured', 'is_active', 'created_at')
    list_filter = ('is_featured', 'is_active', 'parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('sort_order', 'name')

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'sort_order')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'article', 'category', 'price', 'stock_quantity', 'is_published', 'is_active', 'created_at')
    list_filter = ('category', 'is_published', 'is_active', 'is_featured', 'status', 'created_at')
    search_fields = ('name', 'article', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline]
    readonly_fields = ('views_count', 'orders_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'article', 'category')
        }),
        ('Описание', {
            'fields': ('short_description', 'description', 'specifications')
        }),
        ('Цена и склад', {
            'fields': ('price', 'old_price', 'stock_quantity', 'min_stock_level', 'unit')
        }),
        ('Характеристики', {
            'fields': ('weight', 'dimensions', 'material', 'color'),
            'classes': ('collapse',)
        }),
        ('Статус и настройки', {
            'fields': ('status', 'is_published', 'is_featured', 'is_bestseller', 'is_new')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('views_count', 'orders_count', 'published_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )