from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, CompanyProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('user_type', 'phone', 'is_verified', 'avatar', 'birth_date')
        }),
        ('Настройки уведомлений', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Аналитика', {
            'fields': ('last_login_ip', 'login_count'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('email', 'user_type', 'phone')
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'country', 'language', 'created_at')
    list_filter = ('country', 'language', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'unp', 'legal_form', 'vat_payer', 'user', 'created_at')
    list_filter = ('legal_form', 'vat_payer', 'created_at')
    search_fields = ('company_name', 'unp', 'user__email')
    readonly_fields = ('created_at', 'updated_at')