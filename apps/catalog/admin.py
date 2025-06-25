# apps/catalog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q, F
from django.db import models
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий"""
    
    list_display = [
        'name', 
        'parent', 
        'product_count', 
        'sort_order',
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active', 
        'parent',
        'created_at'
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    # Базовые поля, которые точно есть в модели
    fields = [
        'name', 
        'slug', 
        'description', 
        'parent',
        'sort_order', 
        'is_active'
    ]
    
    readonly_fields = ['product_count']
    
    def product_count(self, obj):
        """Количество товаров в категории"""
        try:
            count = obj.products.filter(is_active=True, is_published=True).count()
            
            # Добавляем товары из подкатегорий
            for child in obj.children.filter(is_active=True):
                count += child.products.filter(is_active=True, is_published=True).count()
            
            if count > 0:
                url = reverse('admin:catalog_product_changelist') + f'?category__id__exact={obj.id}'
                return format_html(
                    '<a href="{}" style="color: #007cba; font-weight: bold;">{} товаров</a>',
                    url, count
                )
            return "0 товаров"
        except:
            return "0 товаров"
    product_count.short_description = "Количество товаров"
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('parent').prefetch_related('children', 'products')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Админка для товаров"""
    
    list_display = [
        'name',
        'article',
        'category',
        'price',
        'stock_quantity',
        'is_published',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'is_active',
        'is_published',
        'unit',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'article',
        'description',
        'short_description'
    ]
    
    prepopulated_fields = {'slug': ('name', 'article')}
    
    list_editable = [
        'price',
        'stock_quantity',
        'is_published',
        'is_active'
    ]
    
    # Упрощенные fieldsets с базовыми полями
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'name',
                'slug',
                'article',
                'category'
            )
        }),
        ('Описание', {
            'fields': (
                'short_description',
                'description',
            )
        }),
        ('Цена и склад', {
            'fields': (
                'price',
                'stock_quantity',
                'min_stock_level',
                'unit'
            )
        }),
        ('Настройки', {
            'fields': (
                'is_active',
                'is_published',
            )
        }),
    )
    
    # Добавляем поля только если они есть в модели
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Проверяем наличие дополнительных полей
        model_fields = [f.name for f in self.model._meta.fields]
        
        if 'is_featured' in model_fields:
            # Добавляем is_featured в отображение и редактирование
            if 'is_featured' not in self.list_display:
                self.list_display = list(self.list_display) + ['is_featured']
            if 'is_featured' not in self.list_editable:
                self.list_editable = list(self.list_editable) + ['is_featured']
            
            # Добавляем в fieldsets
            settings_fields = list(self.fieldsets[3][1]['fields'])
            if 'is_featured' not in settings_fields:
                settings_fields.append('is_featured')
                self.fieldsets = self.fieldsets[:-1] + (
                    ('Настройки', {
                        'fields': tuple(settings_fields)
                    }),
                )
        
        if 'views_count' in model_fields:
            if 'views_count' not in self.readonly_fields:
                self.readonly_fields = list(self.readonly_fields) + ['views_count']
        
        if 'old_price' in model_fields:
            # Обновляем fieldsets для цены
            price_fields = ('price', 'old_price', 'stock_quantity', 'min_stock_level', 'unit')
            self.fieldsets = self.fieldsets[:2] + (
                ('Цена и склад', {
                    'fields': price_fields
                }),
            ) + self.fieldsets[3:]
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = [
        'publish_products',
        'unpublish_products',
        'activate_products',
        'deactivate_products'
    ]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('category')
    
    # Действия (Actions)
    def publish_products(self, request, queryset):
        """Опубликовать товары"""
        count = queryset.update(is_published=True, is_active=True)
        self.message_user(request, f'{count} товаров опубликовано.')
    publish_products.short_description = "Опубликовать товары"
    
    def unpublish_products(self, request, queryset):
        """Снять с публикации"""
        count = queryset.update(is_published=False)
        self.message_user(request, f'{count} товаров снято с публикации.')
    unpublish_products.short_description = "Снять с публикации"
    
    def activate_products(self, request, queryset):
        """Активировать товары"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} товаров активировано.')
    activate_products.short_description = "Активировать товары"
    
    def deactivate_products(self, request, queryset):
        """Деактивировать товары"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} товаров деактивировано.')
    deactivate_products.short_description = "Деактивировать товары"


# Инлайн для подкатегорий в категориях
class SubCategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    fields = ['name', 'slug', 'sort_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

# Добавляем инлайн к CategoryAdmin
CategoryAdmin.inlines = [SubCategoryInline]

# Дополнительные настройки админки
admin.site.site_header = 'ОАО "ГЗЛиН" - Администрирование'
admin.site.site_title = 'ГЗЛиН Админ'
admin.site.index_title = 'Панель управления'