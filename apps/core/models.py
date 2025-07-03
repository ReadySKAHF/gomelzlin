from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from tinymce.models import HTMLField
import uuid


class TimeStampedModel(models.Model):
    """
    Абстрактная модель с полями created_at и updated_at
    """
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Абстрактная модель с UUID как первичный ключ
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    class Meta:
        abstract = True


class AbstractBaseModel(TimeStampedModel):
    """
    Абстрактная базовая модель с общими полями
    """
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True
    )
    is_active = models.BooleanField(
        _('Активный'),
        default=True,
        help_text=_('Отметьте, чтобы объект был активным')
    )
    
    class Meta:
        abstract = True


class SeoModel(models.Model):
    """
    Абстрактная модель для SEO полей
    """
    meta_title = models.CharField(
        _('SEO заголовок'),
        max_length=255,
        blank=True,
        help_text=_('Заголовок для поисковых систем (до 60 символов)')
    )
    meta_description = models.TextField(
        _('SEO описание'),
        blank=True,
        max_length=160,
        help_text=_('Описание для поисковых систем (до 160 символов)')
    )
    meta_keywords = models.CharField(
        _('SEO ключевые слова'),
        max_length=255,
        blank=True,
        help_text=_('Ключевые слова через запятую')
    )
    
    class Meta:
        abstract = True


class SystemLog(AbstractBaseModel):
    """
    Модель для системных логов
    """
    LOG_LEVELS = [
        ('DEBUG', _('Отладка')),
        ('INFO', _('Информация')),
        ('WARNING', _('Предупреждение')),
        ('ERROR', _('Ошибка')),
        ('CRITICAL', _('Критическая ошибка')),
    ]
    
    ACTION_TYPES = [
        ('CREATE', _('Создание')),
        ('UPDATE', _('Обновление')),
        ('DELETE', _('Удаление')),
        ('LOGIN', _('Вход в систему')),
        ('LOGOUT', _('Выход из системы')),
        ('ORDER_CREATED', _('Создание заказа')),
        ('ORDER_UPDATED', _('Обновление заказа')),
        ('PAYMENT_SUCCESS', _('Успешная оплата')),
        ('PAYMENT_FAILED', _('Ошибка оплаты')),
        ('PRODUCT_VIEWED', _('Просмотр товара')),
        ('CATEGORY_VIEWED', _('Просмотр категории')),
        ('SEARCH', _('Поиск')),
        ('EXPORT', _('Экспорт данных')),
        ('IMPORT', _('Импорт данных')),
        ('BACKUP', _('Резервное копирование')),
        ('SETTINGS_CHANGED', _('Изменение настроек')),
        ('LOW_STOCK', _('Низкий остаток товара')),
        ('SYSTEM_ERROR', _('Системная ошибка')),
    ]
    
    level = models.CharField(
        _('Уровень'),
        max_length=20,
        choices=LOG_LEVELS,
        default='INFO'
    )
    action_type = models.CharField(
        _('Тип действия'),
        max_length=50,
        choices=ACTION_TYPES
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Пользователь')
    )
    ip_address = models.GenericIPAddressField(
        _('IP-адрес'),
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        _('User Agent'),
        blank=True
    )
    message = models.TextField(_('Сообщение'))
    extra_data = models.JSONField(
        _('Дополнительные данные'),
        blank=True,
        default=dict
    )
    
    class Meta:
        verbose_name = _('Системный лог')
        verbose_name_plural = _('Системные логи')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['level', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.get_level_display()}: {self.action_type} - {self.message[:50]}'


class SiteSettings(models.Model):
    """
    Настройки сайта
    """
    company_name = models.CharField(
        _('Название компании'),
        max_length=255,
        default='ОАО "Гомельский завод литейных изделий и нормалей"'
    )
    company_short_name = models.CharField(
        _('Короткое название'),
        max_length=50,
        default='ГЗЛиН'
    )
    company_description = models.TextField(
        _('Описание компании'),
        blank=True
    )
    
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        default='+375 232 12-34-56'
    )
    email = models.EmailField(
        _('Email'),
        default='info@gomelzlin.by'
    )
    address = models.TextField(
        _('Адрес'),
        default='246000, г. Гомель, ул. Промышленная, 15'
    )
    
    working_hours = models.TextField(
        _('Режим работы'),
        default='Пн-Пт: 8:00-17:00\nСб-Вс: выходной'
    )
    
    facebook_url = models.URLField(_('Facebook'), blank=True)
    instagram_url = models.URLField(_('Instagram'), blank=True)
    youtube_url = models.URLField(_('YouTube'), blank=True)
    
    min_order_amount = models.DecimalField(
        _('Минимальная сумма заказа'),
        max_digits=10,
        decimal_places=2,
        default=100.00
    )
    cart_reservation_time = models.PositiveIntegerField(
        _('Время резерва товара в корзине (минуты)'),
        default=60
    )
    
    order_notification_email = models.EmailField(
        _('Email для уведомлений о заказах'),
        default='orders@gomelzlin.by'
    )
    admin_notification_email = models.EmailField(
        _('Email администратора'),
        default='admin@gomelzlin.by'
    )
    
    site_keywords = models.TextField(
        _('Ключевые слова сайта'),
        blank=True,
        help_text=_('Через запятую')
    )
    google_analytics_id = models.CharField(
        _('Google Analytics ID'),
        max_length=20,
        blank=True
    )
    yandex_metrika_id = models.CharField(
        _('Yandex Metrika ID'),
        max_length=20,
        blank=True
    )
    
    maintenance_mode = models.BooleanField(
        _('Режим технического обслуживания'),
        default=False
    )
    maintenance_message = models.TextField(
        _('Сообщение о техническом обслуживании'),
        blank=True,
        default='Сайт временно недоступен в связи с техническим обслуживанием.'
    )
    
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Настройки сайта')
        verbose_name_plural = _('Настройки сайта')
    
    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('Может существовать только одна запись настроек сайта')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_settings(cls):
        """Получить настройки сайта (создать, если не существуют)"""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings


class ContactMessage(AbstractBaseModel):
    """
    Сообщения с формы обратной связи
    """
    name = models.CharField(_('Имя'), max_length=100)
    email = models.EmailField(_('Email'))
    phone = models.CharField(_('Телефон'), max_length=20, blank=True)
    subject = models.CharField(_('Тема'), max_length=200)
    message = models.TextField(_('Сообщение'))
    is_read = models.BooleanField(_('Прочитано'), default=False)
    
    class Meta:
        verbose_name = _('Сообщение с формы обратной связи')
        verbose_name_plural = _('Сообщения с формы обратной связи')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.name} - {self.subject}'

class News(AbstractBaseModel, SeoModel):
    """
    Модель новостей компании с поддержкой форматированного текста
    """
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('published', _('Опубликовано')),
        ('archived', _('Архив')),
    ]
    
    title = models.CharField(
        _('Заголовок'),
        max_length=255
    )
    slug = models.SlugField(
        _('URL'),
        max_length=255,
        unique=True,
        help_text=_('Автоматически генерируется из заголовка')
    )
    short_description = HTMLField(
        _('Краткое описание'),
        help_text=_('Краткое описание для списка новостей')
    )
    content = HTMLField(
        _('Полное содержание'),
        help_text=_('Полный текст новости с форматированием')
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='news/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Основное изображение новости')
    )
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_featured = models.BooleanField(
        _('Рекомендуемая'),
        default=False,
        help_text=_('Отображается на главной странице')
    )
    published_at = models.DateTimeField(
        _('Дата публикации'),
        blank=True,
        null=True,
        help_text=_('Оставьте пустым для автоматической установки при публикации')
    )
    views_count = models.PositiveIntegerField(
        _('Количество просмотров'),
        default=0
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Автор'),
        related_name='news_articles'
    )
    
    class Meta:
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'is_active']),
            models.Index(fields=['published_at']),
            models.Index(fields=['is_featured', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = 'news'
            
            slug = base_slug
            counter = 1
            while News.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Возвращает URL для детального просмотра новости"""
        return f'/news/{self.slug}/'
    
    def get_short_description_text(self):
        """Возвращает краткое описание без HTML тегов для мета-тегов"""
        if self.short_description:
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.short_description)
            return clean_content
        return ''
    
    def get_short_description(self):
        """Возвращает краткое описание для отображения в списках"""
        if self.short_description:
            return self.short_description
        
        if self.content:
            import re
            clean_content = re.sub(r'<[^>]+>', '', self.content)
            return clean_content[:150] + '...' if len(clean_content) > 150 else clean_content
        
        return ''
    
    def increment_views(self):
        """Увеличивает счетчик просмотров"""
        self.views_count = models.F('views_count') + 1
        self.save(update_fields=['views_count'])
    
    @classmethod
    def get_published(cls):
        """Возвращает только опубликованные активные новости"""
        return cls.objects.filter(
            status='published',
            is_active=True,
            published_at__isnull=False
        )
    
    @classmethod
    def get_featured(cls, limit=3):
        """Возвращает рекомендуемые новости для главной страницы"""
        return cls.get_published().filter(
            is_featured=True
        ).order_by('-published_at')[:limit]