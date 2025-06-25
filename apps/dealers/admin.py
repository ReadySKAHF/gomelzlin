from django.contrib import admin
from .models import DealerCenter

@admin.register(DealerCenter)
class DealerCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'dealer_type', 'contact_person', 'phone', 'is_featured', 'is_active')
    list_filter = ('dealer_type', 'region', 'is_featured', 'is_verified', 'is_active', 'created_at')
    search_fields = ('name', 'city', 'contact_person', 'phone', 'email')
    readonly_fields = ('dealer_code', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'full_name', 'dealer_type', 'dealer_code')
        }),
        ('Контактная информация', {
            'fields': ('contact_person', 'position', 'phone', 'email', 'website')
        }),
        ('Адрес', {
            'fields': ('region', 'city', 'address', 'postal_code')
        }),
        ('Координаты', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Дополнительная информация', {
            'fields': ('working_hours', 'description')
        }),
        ('Настройки отображения', {
            'fields': ('is_featured', 'is_verified', 'sort_order')
        }),
    )