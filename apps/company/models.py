from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from apps.core.models import AbstractBaseModel, SeoModel


class CompanyInfo(AbstractBaseModel, SeoModel):
    """
    Основная информация о компании
    """
    # Основная информация
    full_name = models.CharField(
        _('Полное наименование'),
        max_length=500,
        default='Открытое акционерное общество "Гомельский завод литейных изделий и нормалей"'
    )
    short_name = models.CharField(
        _('Краткое наименование'),
        max_length=100,
        default='ОАО "ГЗЛиН"'
    )
    brand_name = models.CharField(
        _('Торговая марка'),
        max_length=100,
        default='ГЗЛиН'
    )
    
    founded_year = models.PositiveIntegerField(
        _('Год основания'),
        default=1965
    )
    history = models.TextField(
        _('История компании'),
        blank=True
    )
    
    mission = models.TextField(
        _('Миссия'),
        blank=True
    )
    vision = models.TextField(
        _('Видение'),
        blank=True
    )
    values = models.TextField(
        _('Ценности'),
        blank=True,
        help_text=_('Каждая ценность с новой строки')
    )
    
    description = models.TextField(
        _('Описание деятельности'),
        blank=True
    )
    main_activities = models.TextField(
        _('Основные виды деятельности'),
        blank=True,
        help_text=_('Каждый вид деятельности с новой строки')
    )
    
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        default='+375 232 12-34-56'
    )
    fax = models.CharField(
        _('Факс'),
        max_length=20,
        blank=True
    )
    email = models.EmailField(
        _('Email'),
        default='info@gomelzlin.by'
    )
    website = models.URLField(
        _('Веб-сайт'),
        blank=True
    )
    
    legal_address = models.TextField(
        _('Юридический адрес'),
        default='246000, г. Гомель, ул. Промышленная, 15'
    )
    postal_address = models.TextField(
        _('Почтовый адрес'),
        blank=True
    )
    
    working_hours = models.TextField(
        _('Режим работы'),
        default='Пн-Пт: 8:00-17:00\nСб-Вс: выходной'
    )
    
    facebook_url = models.URLField(_('Facebook'), blank=True)
    instagram_url = models.URLField(_('Instagram'), blank=True)
    youtube_url = models.URLField(_('YouTube'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn'), blank=True)
    vk_url = models.URLField(_('ВКонтакте'), blank=True)
    
    unp = models.CharField(
        _('УНП'),
        max_length=9,
        default='400123456',
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message=_('УНП должен содержать 9 цифр')
            )
        ]
    )
    registration_number = models.CharField(
        _('Регистрационный номер'),
        max_length=50,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Информация о компании')
        verbose_name_plural = _('Информация о компании')
    
    def __str__(self):
        return self.short_name
    
    def save(self, *args, **kwargs):
        if not self.pk and CompanyInfo.objects.exists():
            raise ValueError('Может существовать только одна запись информации о компании')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_info(cls):
        """Получить информацию о компании (создать, если не существует)"""
        info, created = cls.objects.get_or_create(pk=1)
        return info


class Leader(AbstractBaseModel):
    """
    Руководство компании
    """
    POSITION_TYPES = [
        ('director', _('Директор')),
        ('deputy_director', _('Заместитель директора')),
        ('chief', _('Начальник')),
        ('manager', _('Менеджер')),
        ('specialist', _('Специалист')),
    ]
    
    first_name = models.CharField(
        _('Имя'),
        max_length=50
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=50
    )
    middle_name = models.CharField(
        _('Отчество'),
        max_length=50,
        blank=True
    )
    
    position = models.CharField(
        _('Должность'),
        max_length=100
    )
    position_type = models.CharField(
        _('Тип должности'),
        max_length=20,
        choices=POSITION_TYPES,
        default='specialist'
    )
    department = models.CharField(
        _('Отдел/Подразделение'),
        max_length=100,
        blank=True
    )
    
    email = models.EmailField(
        _('Email'),
        blank=True
    )
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        blank=True
    )
    
    bio = models.TextField(
        _('Биография'),
        blank=True
    )
    
    photo = models.ImageField(
        _('Фотография'),
        upload_to='company/leaders/',
        blank=True,
        null=True
    )
    
    is_public = models.BooleanField(
        _('Показывать на сайте'),
        default=True
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )
    
    class Meta:
        verbose_name = _('Руководитель')
        verbose_name_plural = _('Руководство')
        ordering = ['sort_order', 'position_type', 'last_name']
    
    def __str__(self):
        return f'{self.get_full_name()} - {self.position}'
    
    def get_full_name(self):
        """Возвращает полное имя"""
        parts = [self.last_name, self.first_name, self.middle_name]
        return ' '.join(filter(None, parts))
    
class Partner(AbstractBaseModel):
    """
    Партнеры компании
    """
    PARTNER_TYPES = [
        ('strategic', _('Стратегический партнер')),
        ('supplier', _('Поставщик')),
        ('customer', _('Клиент')),
        ('distributor', _('Дистрибьютор')),
        ('technology', _('Технологический партнер')),
    ]
    
    name = models.CharField(
        _('Название организации'),
        max_length=255
    )
    full_name = models.CharField(
        _('Полное название'),
        max_length=500,
        blank=True
    )
    description = models.TextField(
        _('Описание'),
        max_length=500,
        help_text=_('Краткое описание партнерства или деятельности компании')
    )
    
    partner_type = models.CharField(
        _('Тип партнерства'),
        max_length=20,
        choices=PARTNER_TYPES,
        default='strategic'
    )
    
    website = models.URLField(
        _('Веб-сайт'),
        blank=True
    )
    email = models.EmailField(
        _('Email'),
        blank=True
    )
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        blank=True
    )
    
    logo = models.ImageField(
        _('Логотип'),
        upload_to='company/partners/',
        blank=True,
        null=True,
        help_text=_('Рекомендуемый размер: 300x200 пикселей')
    )
    
    country = models.CharField(
        _('Страна'),
        max_length=100,
        default='Беларусь'
    )
    city = models.CharField(
        _('Город'),
        max_length=100,
        blank=True
    )
    address = models.TextField(
        _('Адрес'),
        blank=True
    )
    
    partnership_start_date = models.DateField(
        _('Дата начала сотрудничества'),
        blank=True,
        null=True
    )
    cooperation_areas = models.TextField(
        _('Области сотрудничества'),
        blank=True,
        help_text=_('Описание основных направлений сотрудничества')
    )
    
    is_featured = models.BooleanField(
        _('Рекомендуемый партнер'),
        default=False,
        help_text=_('Будет отображаться в приоритетном порядке')
    )
    is_public = models.BooleanField(
        _('Показывать на сайте'),
        default=True
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )
    
    class Meta:
        verbose_name = _('Партнер')
        verbose_name_plural = _('Партнеры')
        ordering = ['-is_featured', 'sort_order', 'name']
        indexes = [
            models.Index(fields=['is_active', 'is_public']),
            models.Index(fields=['is_featured', 'sort_order']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_short_description(self):
        """Возвращает краткое описание (первые 100 символов)"""
        if len(self.description) <= 100:
            return self.description
        return self.description[:97] + '...'