from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
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
    Базовая абстрактная модель для всех моделей приложения
    """
    is_active = models.BooleanField(_('Активно'), default=True)
    
    class Meta:
        abstract = True


class SeoModel(models.Model):
    """
    Абстрактная модель для SEO полей
    """
    meta_title = models.CharField(
        _('Meta Title'),
        max_length=60,
        blank=True,
        help_text=_('Оптимальная длина: 50-60 символов')
    )
    meta_description = models.CharField(
        _('Meta Description'),
        max_length=160,
        blank=True,
        help_text=_('Оптимальная длина: 150-160 символов')
    )
    meta_keywords = models.CharField(
        _('Meta Keywords'),
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
    # Используем строковую ссылку на User модель вместо прямого импорта
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
    
    # Контактная информация
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
    
    # Режим работы
    working_hours = models.TextField(
        _('Режим работы'),
        default='Пн-Пт: 8:00-17:00\nСб-Вс: выходной'
    )
    
    # Социальные сети
    facebook_url = models.URLField(_('Facebook'), blank=True)
    instagram_url = models.URLField(_('Instagram'), blank=True)
    youtube_url = models.URLField(_('YouTube'), blank=True)
    
    # Настройки корзины
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
    
    # Настройки уведомлений
    order_notification_email = models.EmailField(
        _('Email для уведомлений о заказах'),
        default='orders@gomelzlin.by'
    )
    admin_notification_email = models.EmailField(
        _('Email администратора'),
        default='admin@gomelzlin.by'
    )
    
    # SEO настройки
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
    
    # Техническое обслуживание
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
        # Обеспечиваем, что существует только одна запись настроек
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