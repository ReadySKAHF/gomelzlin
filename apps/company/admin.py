from django.contrib import admin
from .models import CompanyInfo, Leader

@admin.register(CompanyInfo)
class CompanyInfoAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'phone', 'email', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'short_name', 'brand_name', 'founded_year')
        }),
        ('История и миссия', {
            'fields': ('history', 'mission', 'vision', 'values', 'description', 'main_activities'),
            'classes': ('collapse',)
        }),
        ('Контактная информация', {
            'fields': ('phone', 'fax', 'email', 'website')
        }),
        ('Адрес', {
            'fields': ('legal_address', 'postal_address', 'working_hours')
        }),
        ('Социальные сети', {
            'fields': ('facebook_url', 'instagram_url', 'youtube_url', 'linkedin_url', 'vk_url'),
            'classes': ('collapse',)
        }),
        ('Регистрационные данные', {
            'fields': ('unp', 'registration_number'),
            'classes': ('collapse',)
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return not CompanyInfo.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Leader)
class LeaderAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'position', 'position_type', 'email', 'is_public', 'sort_order')
    list_filter = ('position_type', 'is_public', 'created_at')
    search_fields = ('first_name', 'last_name', 'position', 'email')
    ordering = ('sort_order', 'position_type', 'last_name')
    
    fieldsets = (
        ('Личная информация', {
            'fields': ('first_name', 'last_name', 'middle_name', 'photo')
        }),
        ('Должность', {
            'fields': ('position', 'position_type', 'department')
        }),
        ('Контактная информация', {
            'fields': ('email', 'phone')
        }),
        ('Дополнительная информация', {
            'fields': ('bio',),
            'classes': ('collapse',)
        }),
        ('Настройки отображения', {
            'fields': ('is_public', 'sort_order')
        }),
    )