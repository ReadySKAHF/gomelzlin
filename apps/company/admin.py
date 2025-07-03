from django.contrib import admin
from .models import CompanyInfo, Leader, Partner

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

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'partner_type', 'city', 'country', 'is_featured', 'is_public', 'sort_order', 'website')
    list_filter = ('partner_type', 'is_featured', 'is_public', 'country', 'created_at')
    search_fields = ('name', 'full_name', 'description', 'city')
    ordering = ('-is_featured', 'sort_order', 'name')
    list_editable = ('is_featured', 'is_public', 'sort_order')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'full_name', 'description', 'partner_type')
        }),
        ('Контактная информация', {
            'fields': ('website', 'email', 'phone')
        }),
        ('Логотип', {
            'fields': ('logo',)
        }),
        ('Адрес', {
            'fields': ('country', 'city', 'address')
        }),
        ('Информация о сотрудничестве', {
            'fields': ('partnership_start_date', 'cooperation_areas'),
            'classes': ('collapse',)
        }),
        ('Настройки отображения', {
            'fields': ('is_featured', 'is_public', 'sort_order')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
    
    def logo_preview(self, obj):
        if obj.logo:
            return f'<img src="{obj.logo.url}" style="max-height: 50px; max-width: 100px;">'
        return 'Нет логотипа'
    logo_preview.allow_tags = True
    logo_preview.short_description = 'Предпросмотр логотипа'