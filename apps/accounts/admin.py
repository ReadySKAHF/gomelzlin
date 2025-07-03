from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, CompanyProfile, DeliveryAddress


class DeliveryAddressInline(admin.TabularInline):
    model = DeliveryAddress
    extra = 0
    fields = ('title', 'city', 'address', 'is_default', 'is_active')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'user_type', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_verified', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    inlines = [DeliveryAddressInline]  # Перенесли сюда, так как DeliveryAddress связана с User
    
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
    # Убрали DeliveryAddressInline отсюда
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'middle_name', 'position', 'department')
        }),
        ('Адресная информация', {
            'fields': ('country', 'city', 'address', 'postal_code')
        }),
        ('Дополнительные контакты', {
            'fields': ('additional_phone', 'skype', 'telegram'),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('language', 'timezone'),
            'classes': ('collapse',)
        }),
        ('Уведомления', {
            'fields': ('order_status_notifications', 'new_products_notifications', 'special_offers_notifications'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'unp', 'legal_form', 'vat_payer', 'user', 'created_at')
    list_filter = ('legal_form', 'vat_payer', 'created_at')
    search_fields = ('company_name', 'unp', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'company_name', 'legal_form')
        }),
        ('Регистрационные данные', {
            'fields': ('unp', 'registration_date', 'registration_authority')
        }),
        ('Адресная информация', {
            'fields': ('legal_address', 'postal_address')
        }),
        ('Банковские реквизиты', {
            'fields': ('bank_name', 'bank_code', 'bank_account'),
            'classes': ('collapse',)
        }),
        ('Налогообложение', {
            'fields': ('vat_payer', 'vat_number'),
            'classes': ('collapse',)
        }),
        ('Контактная информация', {
            'fields': ('contact_person', 'contact_phone', 'contact_email'),
            'classes': ('collapse',)
        }),
        ('Служебная информация', {
            'fields': ('notes', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'city', 'get_short_address', 'is_default', 'is_active', 'created_at')
    list_filter = ('is_default', 'is_active', 'country', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'title', 'city', 'address')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title')
        }),
        ('Адрес', {
            'fields': ('country', 'city', 'address', 'postal_code')
        }),
        ('Контактная информация', {
            'fields': ('contact_person', 'contact_phone')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'is_default', 'is_active')
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_short_address(self, obj):
        return obj.get_short_address()
    get_short_address.short_description = 'Адрес'
    
    def save_model(self, request, obj, form, change):
        # Если устанавливается адрес по умолчанию, убираем флаг у других адресов пользователя
        if obj.is_default:
            DeliveryAddress.objects.filter(
                user=obj.user, 
                is_default=True
            ).exclude(pk=obj.pk).update(is_default=False)
        super().save_model(request, obj, form, change)
    
    actions = ['make_default', 'make_active', 'make_inactive']
    
    def make_default(self, request, queryset):
        for address in queryset:
            # Убираем флаг по умолчанию у других адресов пользователя
            DeliveryAddress.objects.filter(
                user=address.user, 
                is_default=True
            ).update(is_default=False)
            # Устанавливаем новый адрес по умолчанию
            address.is_default = True
            address.save()
        self.message_user(request, f"Установлено {queryset.count()} адресов по умолчанию.")
    make_default.short_description = "Сделать адресом по умолчанию"
    
    def make_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"Активировано {queryset.count()} адресов.")
    make_active.short_description = "Активировать адреса"
    
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False, is_default=False)
        self.message_user(request, f"Деактивировано {queryset.count()} адресов.")
    make_inactive.short_description = "Деактивировать адреса"