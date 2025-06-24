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
    
    # История
    founded_year = models.PositiveIntegerField(
        _('Год основания'),
        default=1965
    )
    history = models.TextField(
        _('История компании'),
        blank=True
    )
    
    # Миссия и ценности
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
    
    # Описание деятельности
    description = models.TextField(
        _('Описание деятельности'),
        blank=True
    )
    main_activities = models.TextField(
        _('Основные виды деятельности'),
        blank=True,
        help_text=_('Каждый вид деятельности с новой строки')
    )
    
    # Достижения
    achievements = models.TextField(
        _('Достижения и награды'),
        blank=True,
        help_text=_('Каждое достижение с новой строки')
    )
    certificates = models.TextField(
        _('Сертификаты и лицензии'),
        blank=True,
        help_text=_('Каждый сертификат с новой строки')
    )
    
    # Статистика
    employee_count = models.PositiveIntegerField(
        _('Количество сотрудников'),
        default=0
    )
    production_capacity = models.CharField(
        _('Производственная мощность'),
        max_length=200,
        blank=True
    )
    export_countries = models.TextField(
        _('Страны экспорта'),
        blank=True,
        help_text=_('Страны через запятую')
    )
    
    # Контакты
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
    
    # Адрес
    legal_address = models.TextField(
        _('Юридический адрес'),
        default='246000, г. Гомель, ул. Промышленная, 15'
    )
    postal_address = models.TextField(
        _('Почтовый адрес'),
        blank=True
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
    linkedin_url = models.URLField(_('LinkedIn'), blank=True)
    vk_url = models.URLField(_('ВКонтакте'), blank=True)
    
    # Регистрационные данные
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
    
    # Банковские реквизиты
    bank_account = models.CharField(
        _('Расчетный счет'),
        max_length=28,
        blank=True
    )
    bank_name = models.CharField(
        _('Наименование банка'),
        max_length=255,
        blank=True
    )
    bank_code = models.CharField(
        _('БИК банка'),
        max_length=8,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Информация о компании')
        verbose_name_plural = _('Информация о компании')
    
    def __str__(self):
        return self.short_name
    
    def save(self, *args, **kwargs):
        # Обеспечиваем единственность записи
        if not self.pk and CompanyInfo.objects.exists():
            raise ValueError('Может существовать только одна запись информации о компании')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_info(cls):
        """Получить информацию о компании (создать, если не существует)"""
        info, created = cls.objects.get_or_create(pk=1)
        return info
    
    def get_values_list(self):
        """Возвращает список ценностей"""
        if self.values:
            return [value.strip() for value in self.values.split('\n') if value.strip()]
        return []
    
    def get_activities_list(self):
        """Возвращает список видов деятельности"""
        if self.main_activities:
            return [activity.strip() for activity in self.main_activities.split('\n') if activity.strip()]
        return []
    
    def get_achievements_list(self):
        """Возвращает список достижений"""
        if self.achievements:
            return [achievement.strip() for achievement in self.achievements.split('\n') if achievement.strip()]
        return []
    
    def get_export_countries_list(self):
        """Возвращает список стран экспорта"""
        if self.export_countries:
            return [country.strip() for country in self.export_countries.split(',') if country.strip()]
        return []


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
    
    # Личная информация
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
    
    # Должность
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
    
    # Контакты
    email = models.EmailField(
        _('Email'),
        blank=True
    )
    phone = models.CharField(
        _('Телефон'),
        max_length=20,
        blank=True
    )
    
    # Дополнительная информация
    bio = models.TextField(
        _('Биография'),
        blank=True
    )
    education = models.TextField(
        _('Образование'),
        blank=True
    )
    experience = models.TextField(
        _('Опыт работы'),
        blank=True
    )
    achievements = models.TextField(
        _('Достижения'),
        blank=True
    )
    
    # Фото
    photo = models.ImageField(
        _('Фотография'),
        upload_to='company/leaders/',
        blank=True,
        null=True
    )
    
    # Настройки отображения
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
    
    def get_initials(self):
        """Возвращает инициалы"""
        initials = self.first_name[0] if self.first_name else ''
        if self.middle_name:
            initials += self.middle_name[0]
        return initials


class Partner(AbstractBaseModel):
    """
    Партнеры компании
    """
    PARTNER_TYPES = [
        ('supplier', _('Поставщик')),
        ('client', _('Клиент')),
        ('distributor', _('Дистрибьютор')),
        ('partner', _('Партнер')),
        ('investor', _('Инвестор')),
    ]
    
    # Основная информация
    name = models.CharField(
        _('Название'),
        max_length=255
    )
    full_name = models.CharField(
        _('Полное название'),
        max_length=500,
        blank=True
    )
    partner_type = models.CharField(
        _('Тип партнера'),
        max_length=20,
        choices=PARTNER_TYPES,
        default='partner'
    )
    
    # Контакты
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
    
    # Адрес
    country = models.CharField(
        _('Страна'),
        max_length=50,
        blank=True
    )
    city = models.CharField(
        _('Город'),
        max_length=50,
        blank=True
    )
    address = models.TextField(
        _('Адрес'),
        blank=True
    )
    
    # Описание
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    cooperation_areas = models.TextField(
        _('Области сотрудничества'),
        blank=True,
        help_text=_('Каждая область с новой строки')
    )
    
    # Логотип
    logo = models.ImageField(
        _('Логотип'),
        upload_to='company/partners/',
        blank=True,
        null=True
    )
    
    # Настройки отображения
    is_featured = models.BooleanField(
        _('Рекомендуемый'),
        default=False,
        help_text=_('Отображать на главной странице')
    )
    is_public = models.BooleanField(
        _('Показывать на сайте'),
        default=True
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )
    
    # Даты сотрудничества
    cooperation_start = models.DateField(
        _('Начало сотрудничества'),
        blank=True,
        null=True
    )
    cooperation_end = models.DateField(
        _('Окончание сотрудничества'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Партнер')
        verbose_name_plural = _('Партнеры')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active_partner(self):
        """Проверяет, активен ли партнер"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.cooperation_end and self.cooperation_end < today:
            return False
        return True
    
    def get_cooperation_areas_list(self):
        """Возвращает список областей сотрудничества"""
        if self.cooperation_areas:
            return [area.strip() for area in self.cooperation_areas.split('\n') if area.strip()]
        return []


class CompanyImage(AbstractBaseModel):
    """
    Изображения компании (офис, производство, мероприятия)
    """
    IMAGE_TYPES = [
        ('office', _('Офис')),
        ('production', _('Производство')),
        ('team', _('Команда')),
        ('event', _('Мероприятие')),
        ('product', _('Продукция')),
        ('certificate', _('Сертификат')),
        ('other', _('Другое')),
    ]
    
    title = models.CharField(
        _('Название'),
        max_length=200
    )
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='company/gallery/'
    )
    image_type = models.CharField(
        _('Тип изображения'),
        max_length=20,
        choices=IMAGE_TYPES,
        default='other'
    )
    alt_text = models.CharField(
        _('Альтернативный текст'),
        max_length=255,
        blank=True
    )
    
    # Настройки отображения
    is_featured = models.BooleanField(
        _('Рекомендуемое'),
        default=False
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
        verbose_name = _('Изображение компании')
        verbose_name_plural = _('Изображения компании')
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return self.title


class CompanyPolicy(AbstractBaseModel):
    """
    Политики компании (кадровая, социальная и т.д.)
    """
    POLICY_TYPES = [
        ('hr', _('Кадровая политика')),
        ('social', _('Социальная политика')),
        ('quality', _('Политика качества')),
        ('environmental', _('Экологическая политика')),
        ('security', _('Политика безопасности')),
        ('privacy', _('Политика конфиденциальности')),
        ('other', _('Другое')),
    ]
    
    title = models.CharField(
        _('Название'),
        max_length=200
    )
    policy_type = models.CharField(
        _('Тип политики'),
        max_length=20,
        choices=POLICY_TYPES,
        default='other'
    )
    content = models.TextField(
        _('Содержание')
    )
    
    # Настройки отображения
    is_public = models.BooleanField(
        _('Показывать на сайте'),
        default=True
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )
    
    # Даты действия
    effective_from = models.DateField(
        _('Действует с'),
        blank=True,
        null=True
    )
    effective_to = models.DateField(
        _('Действует до'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Политика компании')
        verbose_name_plural = _('Политики компании')
        ordering = ['sort_order', 'title']
    
    def __str__(self):
        return self.title
    
    @property
    def is_current(self):
        """Проверяет, действует ли политика в настоящее время"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.effective_from and self.effective_from > today:
            return False
        if self.effective_to and self.effective_to < today:
            return False
        return True