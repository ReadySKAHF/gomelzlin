from django.contrib import admin
from .models import Customer, CustomerTag, CustomerTagAssignment, CustomerNote

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('contact_name', 'email', 'customer_type', 'status', 'city', 'total_orders', 'total_spent', 'created_at')
    list_filter = ('customer_type', 'status', 'country', 'city', 'created_at')
    search_fields = ('contact_name', 'email', 'phone', 'city')
    readonly_fields = ('total_orders', 'total_spent', 'average_order_value', 'last_order_date', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'customer_type', 'status')
        }),
        ('Контактная информация', {
            'fields': ('contact_name', 'email', 'phone', 'additional_phone')
        }),
        ('Адресная информация', {
            'fields': ('country', 'region', 'city', 'address', 'postal_code')
        }),
        ('Коммерческая информация', {
            'fields': ('discount_type', 'discount_value', 'credit_limit', 'payment_terms')
        }),
        ('Метрики', {
            'fields': ('total_orders', 'total_spent', 'average_order_value', 'last_order_date'),
            'classes': ('collapse',)
        }),
        ('Дополнительная информация', {
            'fields': ('source', 'assigned_manager', 'notes')
        }),
        ('Настройки уведомлений', {
            'fields': ('email_notifications', 'sms_notifications', 'marketing_consent'),
            'classes': ('collapse',)
        }),
    )

@admin.register(CustomerTag)
class CustomerTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'created_at')
    search_fields = ('name', 'description')

@admin.register(CustomerNote)
class CustomerNoteAdmin(admin.ModelAdmin):
    list_display = ('customer', 'note_type', 'title', 'author', 'is_important', 'created_at')
    list_filter = ('note_type', 'is_important', 'created_at')
    search_fields = ('customer__contact_name', 'customer__email', 'title', 'content')