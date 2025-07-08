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
        'map_preview',
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
        'coordinates_info',
        'map_preview'
    )
    
    list_editable = ('is_featured', 'sort_order')
    list_per_page = 25

    actions = [
        'make_featured', 
        'remove_featured', 
        'activate_dealers', 
        'deactivate_dealers',
        'copy_coordinates_template'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'full_name', 'dealer_type', 'dealer_code'),
            'classes': ('wide',),
            'description': 'Выберите "Главный завод" для производственных объектов'
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
            'fields': ('latitude', 'longitude', 'coordinates_info', 'yandex_maps_link', 'map_preview'),
            'classes': ('collapse',),
            'description': 'Координаты используются для точного отображения на карте. Если координаты не заданы, будет использован поиск по адресу.'
        }),
        ('Дополнительная информация', {
            'fields': ('working_hours', 'description'),
            'classes': ('wide',)
        }),
        ('Настройки отображения', {
            'fields': ('is_featured', 'is_verified', 'is_active', 'sort_order'),
            'classes': ('wide',),
            'description': 'is_featured - показывать в рекомендуемых, sort_order - порядок сортировки (меньше = выше). Заводы автоматически попадают в рекомендуемые.'
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def dealer_type_badge(self, obj):
        """Отображение типа дилера с цветным бэджем"""
        colors = {
            'factory': '#28a745',  
            'official': '#007bff',    
            'authorized': '#17a2b8',  
            'partner': '#ffc107',      
            'distributor': '#6f42c1'   
        }
        color = colors.get(obj.dealer_type, '#6c757d')

        icon = '🏭' if obj.dealer_type == 'factory' else '🏪'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">'
            '{} {}</span>',
            color, icon, obj.dealer_type_display
        )
    dealer_type_badge.short_description = 'Тип дилера'
    dealer_type_badge.admin_order_field = 'dealer_type'
    
    def phone_link(self, obj):
        """Ссылка на телефон"""
        if obj.phone:
            return format_html(
                '<a href="tel:{}" style="color: #28a745; text-decoration: none;">{}</a>',
                obj.phone, obj.phone
            )
        return '-'
    phone_link.short_description = 'Телефон'
    phone_link.admin_order_field = 'phone'
    
    def email_link(self, obj):
        """Ссылка на email"""
        if obj.email:
            return format_html(
                '<a href="mailto:{}" style="color: #007bff; text-decoration: none;">{}</a>',
                obj.email, obj.email
            )
        return '-'
    email_link.short_description = 'Email'
    email_link.admin_order_field = 'email'
    
    def coordinates_status(self, obj):
        """Статус координат"""
        if obj.has_coordinates:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">✓ Есть</span><br>'
                '<small style="color: #6c757d;">Lat: {}, Lng: {}</small>',
                obj.latitude, obj.longitude
            )
        return format_html('<span style="color: #dc3545;">✗ Нет</span>')
    coordinates_status.short_description = 'Координаты'
    
    def map_preview(self, obj):
        """Превью карты"""
        if obj.has_coordinates:
            return format_html(
                '<iframe src="https://yandex.ru/map-widget/v1/?pt={},{}&z=15&l=map" '
                'width="200" height="150" frameborder="0" style="border-radius: 8px;"></iframe>',
                obj.longitude, obj.latitude
            )
        return format_html(
            '<div style="width: 200px; height: 150px; background: #f8f9fa; '
            'border-radius: 8px; display: flex; align-items: center; justify-content: center; '
            'color: #6c757d; font-size: 12px; text-align: center;">'
            'Нет координат<br>для превью</div>'
        )
    map_preview.short_description = 'Превью на карте'
    
    def status_badge(self, obj):
        """Статус активности"""
        if obj.is_active:
            if obj.is_verified:
                badge_color = '#28a745' if obj.dealer_type != 'factory' else '#20c997'
                return format_html(
                    '<span style="background-color: {}; color: white; padding: 2px 6px; '
                    'border-radius: 8px; font-size: 10px;">АКТИВЕН ✓</span>',
                    badge_color
                )
            else:
                return format_html(
                    '<span style="background-color: #ffc107; color: #333; padding: 2px 6px; '
                    'border-radius: 8px; font-size: 10px;">НЕ ВЕРИФИЦИРОВАН</span>'
                )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 2px 6px; '
            'border-radius: 8px; font-size: 10px;">НЕАКТИВЕН</span>'
        )
    status_badge.short_description = 'Статус'
    
    def yandex_maps_link(self, obj):
        """Ссылка на Яндекс карты"""
        if obj.has_coordinates or obj.address:
            map_icon = '🏭' if obj.dealer_type == 'factory' else '🗺️'
            return format_html(
                '<a href="{}" target="_blank" style="background-color: #cb413b; color: white; '
                'padding: 8px 15px; border-radius: 8px; text-decoration: none; font-weight: bold; '
                'display: inline-block; margin-bottom: 10px;">'
                '{} Открыть на Яндекс картах</a><br>'
                '<small style="color: #6c757d;">Откроется в новой вкладке</small>',
                obj.yandex_maps_url, map_icon
            )
        return 'Нет данных для отображения на карте'
    yandex_maps_link.short_description = 'Яндекс карты'
    
    def coordinates_info(self, obj):
        """Информация о координатах"""
        if obj.has_coordinates:
            return format_html(
                '<div style="background: #d4edda; border: 1px solid #c3e6cb; border-radius: 8px; padding: 15px; margin: 10px 0;">'
                '<strong style="color: #155724;">✓ Координаты заданы</strong><br>'
                '<div style="margin: 10px 0;">'
                '📍 <strong>Широта:</strong> {}<br>'
                '📍 <strong>Долгота:</strong> {}'
                '</div>'
                '<small style="color: #6c757d;">'
                'Объект будет показан на карте в точной позиции. '
                'Убедитесь, что координаты указаны правильно.'
                '</small></div>',
                obj.latitude, obj.longitude
            )
        else:
            type_hint = 'завод' if obj.dealer_type == 'factory' else 'дилер'
            return format_html(
                '<div style="background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 8px; padding: 15px; margin: 10px 0;">'
                '<strong style="color: #721c24;">⚠️ Координаты не заданы</strong><br>'
                '<div style="margin: 10px 0;">'
                '<strong>Будет использован поиск по адресу:</strong><br>'
                '📍 {}, {}'
                '</div>'
                '<small style="color: #6c757d;">'
                'Рекомендуется указать точные координаты для корректного отображения {} на карте. '
                'Можете получить координаты на '
                '<a href="https://yandex.by/maps" target="_blank">Яндекс картах</a>.'
                '</small></div>',
                obj.city, obj.address, type_hint
            )
    coordinates_info.short_description = 'Информация о координатах'

    def make_featured(self, request, queryset):
        """Сделать рекомендуемыми"""
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} объектов отмечены как рекомендуемые.')
    make_featured.short_description = '⭐ Отметить как рекомендуемые'
    
    def remove_featured(self, request, queryset):
        """Убрать из рекомендуемых"""
        non_factory_count = queryset.exclude(dealer_type='factory').update(is_featured=False)
        factory_count = queryset.filter(dealer_type='factory').count()
        
        message = f'{non_factory_count} объектов убраны из рекомендуемых.'
        if factory_count > 0:
            message += f' Заводы ({factory_count} шт.) остались рекомендуемыми автоматически.'
        
        self.message_user(request, message)
    remove_featured.short_description = '⭐ Убрать из рекомендуемых'
    
    def activate_dealers(self, request, queryset):
        """Активировать дилеров"""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} объектов активированы.')
    activate_dealers.short_description = '✅ Активировать'
    
    def deactivate_dealers(self, request, queryset):
        """Деактивировать дилеров"""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} объектов деактивированы.')
    deactivate_dealers.short_description = '❌ Деактивировать'
    
    def copy_coordinates_template(self, request, queryset):
        """Шаблон для координат"""
        coordinates_list = []
        for obj in queryset:
            type_icon = '🏭' if obj.dealer_type == 'factory' else '🏪'
            if obj.has_coordinates:
                coordinates_list.append(f"{type_icon} {obj.name}: {obj.latitude}, {obj.longitude}")
            else:
                coordinates_list.append(f"{type_icon} {obj.name}: НЕТ КООРДИНАТ")
        
        self.message_user(
            request, 
            f"Координаты выбранных объектов:\n" + "\n".join(coordinates_list)
        )
    copy_coordinates_template.short_description = '📋 Показать координаты'

    def save_model(self, request, obj, form, change):
        """Автоматические настройки при сохранении"""
        if not obj.dealer_code:
            obj.dealer_code = obj.generate_dealer_code()

        if obj.dealer_type == 'factory':
            obj.is_featured = True
            if obj.sort_order == 0:
                obj.sort_order = 1
        
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Оптимизируем запросы и сортировку"""
        return super().get_queryset(request).select_related().extra(
            select={
                'type_order': """
                    CASE 
                        WHEN dealer_type = 'factory' THEN 0 
                        ELSE 1 
                    END
                """
            }
        ).order_by('type_order', 'sort_order', 'name')
    
    def get_list_filter(self, request):
        """Обновляем фильтры"""
        return (
            ('dealer_type', admin.ChoicesFieldListFilter),
            'region', 
            'is_featured', 
            'is_verified', 
            'is_active', 
            'created_at'
        )
    
    class Media:
        css = {
            'all': (
                'admin/css/custom_dealer_admin.css',
                'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
            )
        }
        js = ('admin/js/dealer_admin.js',)