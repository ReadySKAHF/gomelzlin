from django.contrib import admin
from .models import SiteSettings, ContactMessage, SystemLog

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'phone', 'email', 'updated_at')
    
    def has_add_permission(self, request):
        # Разрешаем создавать только если нет записей
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Запрещаем удаление настроек
        return False

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ('level', 'action_type', 'user', 'message', 'created_at')
    list_filter = ('level', 'action_type', 'created_at')
    search_fields = ('message', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    def has_add_permission(self, request):
        return False  # Логи создаются автоматически
    
    def has_change_permission(self, request, obj=None):
        return False  # Логи нельзя изменять