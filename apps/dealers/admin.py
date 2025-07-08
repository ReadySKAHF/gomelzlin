from django.contrib import admin
from .models import DealerCenter
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

@admin.register(DealerCenter)
class DealerCenterAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'city', 
        'dealer_type_badge', 
        'contact_person', 
        'phone_link', 
        'email_link',
        'coordinates_status',
        'is_featured',
        'sort_order',
        'status_badge'
    )
    list_filter = (
        'dealer_type', 
        'region', 
        'is_featured', 
        'is_verified', 
        'is_active', 
        'created_at'
    )
    search_fields = (
        'name', 
        'full_name',
        'city', 
        'contact_person', 
        'phone', 
        'email',
        'dealer_code'
    )
    readonly_fields = (
        'dealer_code', 
        'created_at', 
        'updated_at',
        'yandex_maps_link',
        'coordinates_info'
    )
    
    list_editable = ('is_featured', 'sort_order')
    list_per_page = 25

    actions = ['make_featured', 'remove_featured', 'activate_dealers', 'deactivate_dealers']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'full_name', 'dealer_type', 'dealer_code'),
            'classes': ('wide',)
        }),
        ('Контактная информация', {
            'fields': ('contact_person', 'position', 'phone', 'email', 'website'),
            'classes': ('wide',)
        }),
        ('Адрес', {
            'fields': ('region', 'city', 'address', 'postal_code'),
            'classes': ('wide',)
        }),
        ('Координаты и карты', {
            'fields': ('latitude', 'longitude', 'coordinates_info', 'yandex_maps_link'),
            'classes': ('collapse',),
            'description': 'Координаты используются для точного отображения на карте'
        }),
        ('Дополнительная информация', {
            'fields': ('working_hours', 'description'),
            'classes': ('wide',)
        }),
        ('Настройки отображения', {
            'fields': ('is_featured', 'is_verified', 'is_active', 'sort_order'),
            'classes': ('wide',)
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def dealer_type_badge(self, obj):
        """Отображение типа дилера с цветным бэджем"""
        colors = {
            'official': '#28a745',   
            'authorized': '#007bff',  
            'partner': '#ffc107',     
            'distributor': '#6f42c1' 
        }
        color = colors.get(obj.dealer_type, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.dealer_type_display
        )
    dealer_type_badge.short_description = 'Тип дилера'
    dealer_type_badge.admin_order_field = 'dealer_type'
    
    def phone_link(self, obj):
        """Ссылка на телефон"""
        if obj.phone:
            return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)
        return '-'
    phone_link.short_description = 'Телефон'
    phone_link.admin_order_field = 'phone'
    
    def email_link(self, obj):
        """Ссылка на email"""
        if obj.email:
            return format_html('<a href="mailto:{}">{}</a>', obj.email, obj.email)
        return '-'
    email_link.short_description = 'Email'
    email_link.admin_order_field = 'email'
    
    def coordinates_status(self, obj):
        """Статус координат"""
        if obj.has_coordinates:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Есть</span>'
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">✗ Нет</span>'
            )
    coordinates_status.short_description = 'Координаты'
    

    
    def status_badge(self, obj):
        """Статус активности"""
        if obj.is_active:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 10px; font-weight: bold;">Активен</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 6px; '
                'border-radius: 10px; font-size: 10px; font-weight: bold;">Неактивен</span>'
            )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'is_active'
    
    def yandex_maps_link(self, obj):
        """Ссылка на Яндекс карты"""
        if obj.has_coordinates or obj.address:
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #cb413b; color: white; '
                'padding: 5px 10px; border-radius: 5px; text-decoration: none; font-weight: bold;">'
                '🗺️ Открыть на Яндекс картах</a>',
                obj.yandex_maps_url
            )
        return 'Нет данных для отображения на карте'
    yandex_maps_link.short_description = 'Яндекс карты'
    
    def coordinates_info(self, obj):
        """Информация о координатах"""
        if obj.has_coordinates:
            return format_html(
                'Широта: <strong>{}</strong><br>'
                'Долгота: <strong>{}</strong><br>'
                '<small style="color: #6c757d;">Координаты заданы, будет показана точная позиция на карте</small>',
                obj.latitude, obj.longitude
            )
        else:
            return format_html(
                '<span style="color: #dc3545;">Координаты не заданы</span><br>'
                '<small style="color: #6c757d;">Будет использован поиск по адресу: {}, {}</small>',
                obj.city, obj.address
            )
    coordinates_info.short_description = 'Информация о координатах'

    def make_featured(self, request, queryset):
        """Сделать рекомендуемыми"""
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} дилеров отмечены как рекомендуемые.')
    make_featured.short_description = 'Отметить как рекомендуемые'
    
    def remove_featured(self, request, queryset):
        """Убрать из рекомендуемых"""
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} дилеров убраны из рекомендуемых.')
    remove_featured.short_description = 'Убрать из рекомендуемых'
    
    def activate_dealers(self, request, queryset):
        """Активировать дилеров"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} дилеров активированы.')
    activate_dealers.short_description = 'Активировать'
    
    def deactivate_dealers(self, request, queryset):
        """Деактивировать дилеров"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} дилеров деактивированы.')
    deactivate_dealers.short_description = 'Деактивировать'
    
    class Media:
        css = {
            'all': ('admin/css/custom_dealer_admin.css',)
        }
        js = ('admin/js/dealer_admin.js',)