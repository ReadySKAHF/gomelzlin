# apps/catalog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q, F
from django.db import models
from .models import Category, Product


# apps/catalog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Q, F
from django.db import models
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админка для категорий с поддержкой популярных категорий"""
    
    list_display = [
        'name', 
        'parent', 
        'product_count', 
        'sort_order',
        'is_featured_display',  # Обновляем для красивого отображения
        'is_active',
        'created_at'
    ]
    list_filter = [
        'is_active', 
        'is_featured',  # Добавляем фильтр по популярности
        'parent',
        'created_at'
    ]
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    readonly_fields = ['product_count']
    
    # Группировка полей для удобства
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Изображение', {
            'fields': ('image',),
            'classes': ('collapse',)
        }),
        ('Структура', {
            'fields': ('parent', 'sort_order')
        }),
        ('Настройки отображения', {
            'fields': ('is_featured', 'is_active'),
            'description': 'is_featured - отображать на главной странице в разделе "Популярные категории"'
        }),
        ('Статистика', {
            'fields': ('product_count',),
            'classes': ('collapse',)
        })
    )
    
    # Действия для массового управления
    actions = ['make_featured', 'make_not_featured', 'activate_categories', 'deactivate_categories']
    
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
    
    def is_featured_display(self, obj):
        """Отображение статуса популярности с иконкой"""
        if hasattr(obj, 'is_featured') and obj.is_featured:
            return format_html('⭐ <span style="color: #28a745;">Популярная</span>')
        return format_html('☆ <span style="color: #6c757d;">Обычная</span>')
    is_featured_display.short_description = "Популярность"
    is_featured_display.admin_order_field = 'is_featured'
    
    # Массовые действия
    def make_featured(self, request, queryset):
        """Отметить как популярные"""
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} категорий отмечено как популярные.')
    make_featured.short_description = "⭐ Отметить как популярные"
    
    def make_not_featured(self, request, queryset):
        """Убрать из популярных"""
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} категорий убрано из популярных.')
    make_not_featured.short_description = "☆ Убрать из популярных"
    
    def activate_categories(self, request, queryset):
        """Активировать категории"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} категорий активировано.')
    activate_categories.short_description = "✅ Активировать категории"
    
    def deactivate_categories(self, request, queryset):
        """Деактивировать категории"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} категорий деактивировано.')
    deactivate_categories.short_description = "❌ Деактивировать категории"
    
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
        'is_featured_display',  # Добавляем отображение рекомендуемых товаров
        'is_published',
        'is_active',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'is_active',
        'is_published',
        'is_featured',  # Добавляем фильтр по рекомендуемым товарам
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
    
    # Обновленные fieldsets с поддержкой is_featured
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
        ('Настройки отображения', {
            'fields': (
                'is_active',
                'is_published',
                'is_featured',  # Добавляем поле рекомендуемых товаров
            ),
            'description': 'is_featured - отображать в рекомендуемых товарах на главной странице'
        }),
    )
    
    # Действия для товаров
    actions = [
        'publish_products', 
        'unpublish_products',
        'make_featured',
        'make_not_featured',
        'activate_products', 
        'deactivate_products'
    ]
    
    def is_featured_display(self, obj):
        """Отображение статуса рекомендуемости с иконкой"""
        if hasattr(obj, 'is_featured') and obj.is_featured:
            return format_html('⭐ <span style="color: #28a745;">Рекомендуемый</span>')
        return format_html('☆ <span style="color: #6c757d;">Обычный</span>')
    is_featured_display.short_description = "Рекомендуемый"
    is_featured_display.admin_order_field = 'is_featured'
    
    def publish_products(self, request, queryset):
        """Опубликовать товары"""
        count = queryset.update(is_published=True)
        self.message_user(request, f'{count} товаров опубликовано.')
    publish_products.short_description = "📢 Опубликовать товары"
    
    def unpublish_products(self, request, queryset):
        """Снять с публикации"""
        count = queryset.update(is_published=False)
        self.message_user(request, f'{count} товаров снято с публикации.')
    unpublish_products.short_description = "📝 Снять с публикации"
    
    def make_featured(self, request, queryset):
        """Отметить как рекомендуемые"""
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} товаров отмечено как рекомендуемые.')
    make_featured.short_description = "⭐ Отметить как рекомендуемые"
    
    def make_not_featured(self, request, queryset):
        """Убрать из рекомендуемых"""
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} товаров убрано из рекомендуемых.')
    make_not_featured.short_description = "☆ Убрать из рекомендуемых"
    
    def activate_products(self, request, queryset):
        """Активировать товары"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} товаров активировано.')
    activate_products.short_description = "✅ Активировать товары"
    
    def deactivate_products(self, request, queryset):
        """Деактивировать товары"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} товаров деактивировано.')
    deactivate_products.short_description = "❌ Деактивировать товары"

# Инлайн для подкатегорий в категориях
class SubCategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    fields = ['name', 'slug', 'sort_order', 'is_featured', 'is_active']
    prepopulated_fields = {'slug': ('name',)}

# Инлайн к CategoryAdmin
CategoryAdmin.inlines = [SubCategoryInline]

# Дополнительные настройки админки
admin.site.site_header = 'ОАО "ГЗЛиН" - Администрирование'
admin.site.site_title = 'ГЗЛиН Админ'
admin.site.index_title = 'Панель управления'