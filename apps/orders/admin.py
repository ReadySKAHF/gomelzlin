from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem, OrderStatusHistory, Wishlist, WishlistItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_article')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('number', 'customer_name', 'customer_email', 'status', 'total_amount', 'is_paid', 'created_at')
    list_filter = ('status', 'is_paid', 'payment_method', 'delivery_method', 'created_at')
    search_fields = ('number', 'customer_name', 'customer_email', 'company_name')
    readonly_fields = ('number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('number', 'user', 'status')
        }),
        ('Контактная информация', {
            'fields': ('customer_name', 'customer_email', 'customer_phone')
        }),
        ('Информация о компании', {
            'fields': ('company_name', 'company_unp', 'company_address'),
            'classes': ('collapse',)
        }),
        ('Доставка', {
            'fields': ('delivery_method', 'delivery_address', 'delivery_date', 'delivery_time', 'delivery_cost')
        }),
        ('Оплата', {
            'fields': ('payment_method', 'is_paid', 'paid_at')
        }),
        ('Суммы', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total_amount')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'admin_notes', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Системная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'items_count', 'total_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__email', 'session_key')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('user__email', 'name')
