from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django import forms
from tinymce.widgets import TinyMCE
from .models import SiteSettings, ContactMessage, SystemLog, News
from django.utils.safestring import mark_safe

class TinyMCEWidget(forms.Textarea):
    """
    Виджет TinyMCE с загрузкой через CDN
    """
    def __init__(self, attrs=None, config='default'):
        default_attrs = {'class': 'tinymce-editor'}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
        self.config = config

    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        # Определяем высоту в зависимости от поля
        height = 200 if 'short_description' in name else 400
        
        # Определяем toolbar в зависимости от поля
        if 'short_description' in name:
            toolbar = 'bold italic underline | forecolor | bullist numlist | removeformat'
            plugins = 'lists'
        else:
            toolbar = 'undo redo | blocks | bold italic underline strikethrough | forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | removeformat | help'
            plugins = 'advlist autolink lists link charmap preview searchreplace visualblocks code fullscreen insertdatetime table help wordcount'
        
        return mark_safe(html + f'''
        <script src="https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.8.2/tinymce.min.js"></script>
        <script>
        document.addEventListener('DOMContentLoaded', function() {{
            if (typeof tinymce !== 'undefined') {{
                tinymce.init({{
                    selector: '#id_{name}',
                    height: {height},
                    plugins: '{plugins}',
                    toolbar: '{toolbar}',
                    content_style: 'body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px }}',
                    paste_as_text: true,
                    menubar: false,
                    branding: false,
                    promotion: false,
                    license_key: 'gpl',
                    setup: function(editor) {{
                        editor.on('change', function() {{
                            editor.save();
                        }});
                    }}
                }});
            }}
        }});
        </script>
        ''')

class NewsAdminForm(forms.ModelForm):
    """
    Форма для админки с TinyMCE виджетами
    """
    short_description = forms.CharField(
        label="Краткое описание",
        widget=TinyMCEWidget(attrs={'rows': 6}, config='minimal'),
        help_text="Краткое описание для списка новостей"
    )
    
    content = forms.CharField(
        label="Полное содержание", 
        widget=TinyMCEWidget(attrs={'rows': 15}, config='full'),
        help_text="Полный текст новости с форматированием"
    )
    
    class Meta:
        model = News
        fields = '__all__'

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
    """
    Админ-панель для просмотра системных логов
    """
    list_display = [
        'level',
        'action_type',
        'message',
        'user',
        'ip_address',
        'created_at'
    ]
    list_filter = [
        'level',
        'action_type',
        'created_at'
    ]
    search_fields = [
        'message',
        'user__username',
        'ip_address'
    ]
    readonly_fields = [
        'created_at',
        'updated_at'
    ]
    
    def has_add_permission(self, request):
        """Запрещаем добавление логов через админку"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Запрещаем изменение логов"""
        return False
    
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    """
    Админ-панель для управления новостями с TinyMCE
    """
    form = NewsAdminForm
    
    list_display = [
        'title', 
        'status_badge', 
        'is_featured_badge',
        'published_at', 
        'views_count',
        'author',
        'created_at'
    ]
    list_filter = [
        'status', 
        'is_featured', 
        'is_active',
        'published_at',
        'created_at'
    ]
    search_fields = [
        'title', 
        'short_description', 
        'content'
    ]
    readonly_fields = [
        'views_count', 
        'created_at', 
        'updated_at'
    ]
    prepopulated_fields = {
        'slug': ('title',)
    }
    
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'title',
                'slug',
                'short_description',
                'content',
                'image'
            )
        }),
        ('Статус и настройки', {
            'fields': (
                'status',
                'is_featured',
                'is_active',
                'published_at',
                'author'
            )
        }),
        ('SEO', {
            'fields': (
                'meta_title',
                'meta_description', 
                'meta_keywords'
            ),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': (
                'views_count',
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = [
        'make_published',
        'make_draft',
        'make_featured',
        'make_not_featured'
    ]
    
    def status_badge(self, obj):
        """Отображение статуса с цветным бейджем"""
        colors = {
            'draft': '#6c757d',
            'published': '#28a745',
            'archived': '#dc3545'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    
    def is_featured_badge(self, obj):
        """Отображение рекомендуемой новости"""
        if obj.is_featured:
            return format_html(
                '<span style="color: #ffc107; font-size: 16px;">⭐</span>'
            )
        return '—'
    is_featured_badge.short_description = 'Рекомендуемая'
    
    def make_published(self, request, queryset):
        """Опубликовать выбранные новости"""
        updated = 0
        for news in queryset:
            if news.status != 'published':
                news.status = 'published'
                if not news.published_at:
                    news.published_at = timezone.now()
                news.save()
                updated += 1
        
        self.message_user(
            request,
            f'Опубликовано новостей: {updated}'
        )
    make_published.short_description = 'Опубликовать выбранные новости'
    
    def make_draft(self, request, queryset):
        """Перевести в черновики"""
        updated = queryset.update(status='draft')
        self.message_user(
            request,
            f'Переведено в черновики: {updated} новостей'
        )
    make_draft.short_description = 'Перевести в черновики'
    
    def make_featured(self, request, queryset):
        """Сделать рекомендуемыми"""
        updated = queryset.update(is_featured=True)
        self.message_user(
            request,
            f'Отмечено как рекомендуемые: {updated} новостей'
        )
    make_featured.short_description = 'Сделать рекомендуемыми'
    
    def make_not_featured(self, request, queryset):
        """Убрать из рекомендуемых"""
        updated = queryset.update(is_featured=False)
        self.message_user(
            request,
            f'Убрано из рекомендуемых: {updated} новостей'
        )
    make_not_featured.short_description = 'Убрать из рекомендуемых'
    
    def save_model(self, request, obj, form, change):
        """Автоматически устанавливаем автора при создании"""
        if not change and not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
