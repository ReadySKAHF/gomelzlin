from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from apps.core.models import AbstractBaseModel


class DealerCenterManager(models.Manager):
    """Менеджер для модели DealerCenter"""
    
    def active(self):
        """Активные дилерские центры"""
        return self.filter(is_active=True)
    
    def by_region(self, region):
        """Дилеры по региону"""
        return self.active().filter(region=region)
    
    def by_city(self, city):
        """Дилеры по городу"""
        return self.active().filter(city__icontains=city)


class DealerCenter(AbstractBaseModel):
    """
    Модель дилерского центра
    """
    DEALER_TYPES = [
        ('official', _('Официальный дилер')),
        ('authorized', _('Авторизованный дилер')),
        ('partner', _('Партнер')),
        ('distributor', _('Дистрибьютор')),
    ]
    
    REGIONS = [
        ('minsk', _('Минская область')),
        ('gomel', _('Гомельская область')),
        ('brest', _('Брестская область')),
        ('vitebsk', _('Витебская область')),
        ('grodno', _('Гродненская область')),
        ('mogilev', _('Могилевская область')),
        ('minsk_city', _('г. Минск')),
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
    dealer_type = models.CharField(
        _('Тип дилера'),
        max_length=20,
        choices=DEALER_TYPES,
        default='partner'
    )
    dealer_code = models.CharField(
        _('Код дилера'),
        max_length=20,
        unique=True,
        blank=True
    )
    
    # Контактная информация
    contact_person = models.CharField(
        _('Контактное лицо'),
        max_length=100
    )
    position = models.CharField(
        _('Должность'),
        max_length=100,
        blank=True
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?375\d{9}$',
        message=_('Номер телефона должен быть в формате: "+375XXXXXXXXX"')
    )
    phone = models.CharField(
        _('Телефон'),
        validators=[phone_regex],
        max_length=13
    )
    additional_phone = models.CharField(
        _('Дополнительный телефон'),
        max_length=13,
        blank=True
    )
    fax = models.CharField(
        _('Факс'),
        max_length=20,
        blank=True
    )
    email = models.EmailField(
        _('Email')
    )
    website = models.URLField(
        _('Веб-сайт'),
        blank=True
    )
    
    # Адрес
    region = models.CharField(
        _('Область'),
        max_length=20,
        choices=REGIONS
    )
    city = models.CharField(
        _('Город'),
        max_length=50
    )
    address = models.TextField(
        _('Адрес')
    )
    postal_code = models.CharField(
        _('Почтовый индекс'),
        max_length=10,
        blank=True
    )
    
    # Координаты для карты
    latitude = models.DecimalField(
        _('Широта'),
        max_digits=10,
        decimal_places=8,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-90),
            MaxValueValidator(90)
        ]
    )
    longitude = models.DecimalField(
        _('Долгота'),
        max_digits=11,
        decimal_places=8,
        blank=True,
        null=True,
        validators=[
            MinValueValidator(-180),
            MaxValueValidator(180)
        ]
    )
    
    # Режим работы
    working_hours = models.TextField(
        _('Режим работы'),
        default='Пн-Пт: 9:00-18:00\nСб: 9:00-15:00\nВс: выходной'
    )
    
    # Услуги и возможности
    services = models.TextField(
        _('Предоставляемые услуги'),
        blank=True,
        help_text=_('Каждая услуга с новой строки')
    )
    product_categories = models.TextField(
        _('Категории товаров'),
        blank=True,
        help_text=_('Категории товаров, которые продает дилер')
    )
    
    # Дополнительные услуги
    has_delivery = models.BooleanField(
        _('Доставка'),
        default=False
    )
    has_installation = models.BooleanField(
        _('Монтаж'),
        default=False
    )
    has_service = models.BooleanField(
        _('Сервисное обслуживание'),
        default=False
    )
    has_warranty = models.BooleanField(
        _('Гарантийное обслуживание'),
        default=False
    )
    has_pickup = models.BooleanField(
        _('Самовывоз'),
        default=True
    )
    
    # Информация о дилере
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    about = models.TextField(
        _('О дилере'),
        blank=True
    )
    experience_years = models.PositiveIntegerField(
        _('Опыт работы (лет)'),
        blank=True,
        null=True
    )
    
    # Изображения
    logo = models.ImageField(
        _('Логотип'),
        upload_to='dealers/logos/',
        blank=True,
        null=True
    )
    main_image = models.ImageField(
        _('Главное изображение'),
        upload_to='dealers/images/',
        blank=True,
        null=True
    )
    
    # Настройки отображения
    is_featured = models.BooleanField(
        _('Рекомендуемый'),
        default=False,
        help_text=_('Отображать в топе списка')
    )
    is_verified = models.BooleanField(
        _('Проверенный'),
        default=False,
        help_text=_('Дилер прошел проверку')
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )
    
    # Рейтинг и отзывы
    rating = models.DecimalField(
        _('Рейтинг'),
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ]
    )
    reviews_count = models.PositiveIntegerField(
        _('Количество отзывов'),
        default=0
    )
    
    # Сроки сотрудничества
    partnership_start = models.DateField(
        _('Начало сотрудничества'),
        blank=True,
        null=True
    )
    partnership_end = models.DateField(
        _('Окончание сотрудничества'),
        blank=True,
        null=True
    )
    
    # Контактная информация для внутреннего использования
    internal_notes = models.TextField(
        _('Внутренние заметки'),
        blank=True
    )
    manager_notes = models.TextField(
        _('Заметки менеджера'),
        blank=True
    )
    
    objects = DealerCenterManager()
    
    class Meta:
        verbose_name = _('Дилерский центр')
        verbose_name_plural = _('Дилерские центры')
        ordering = ['sort_order', 'region', 'city', 'name']
        indexes = [
            models.Index(fields=['region', 'city']),
            models.Index(fields=['dealer_type', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.city})'
    
    def save(self, *args, **kwargs):
        # Автоматическая генерация кода дилера
        if not self.dealer_code:
            self.dealer_code = self.generate_dealer_code()
        super().save(*args, **kwargs)
    
    def generate_dealer_code(self):
        """Генерирует уникальный код дилера"""
        import random
        import string
        
        # Формат: регион(2 символа) + город(2 символа) + номер(3 цифры)
        region_code = self.region[:2].upper()
        city_code = self.city[:2].upper()
        
        # Ищем свободный номер
        for i in range(1, 1000):
            code = f'{region_code}{city_code}{i:03d}'
            if not DealerCenter.objects.filter(dealer_code=code).exists():
                return code
        
        # Если все номера заняты, добавляем случайные символы
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        return f'{region_code}{city_code}{random_part}'
    
    @property
    def full_address(self):
        """Полный адрес дилера"""
        parts = [self.postal_code, self.city, self.address]
        return ', '.join(filter(None, parts))
    
    @property
    def has_coordinates(self):
        """Проверяет наличие координат"""
        return self.latitude is not None and self.longitude is not None
    
    @property
    def is_active_partnership(self):
        """Проверяет активность партнерства"""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.partnership_end and self.partnership_end < today:
            return False
        return True
    
    def get_services_list(self):
        """Возвращает список услуг"""
        if self.services:
            return [service.strip() for service in self.services.split('\n') if service.strip()]
        return []
    
    def get_product_categories_list(self):
        """Возвращает список категорий товаров"""
        if self.product_categories:
            return [category.strip() for category in self.product_categories.split('\n') if category.strip()]
        return []
    
    def get_additional_services(self):
        """Возвращает список дополнительных услуг"""
        services = []
        if self.has_delivery:
            services.append(_('Доставка'))
        if self.has_installation:
            services.append(_('Монтаж'))
        if self.has_service:
            services.append(_('Сервисное обслуживание'))
        if self.has_warranty:
            services.append(_('Гарантийное обслуживание'))
        if self.has_pickup:
            services.append(_('Самовывоз'))
        return services
    
    def update_rating(self):
        """Обновляет рейтинг на основе отзывов"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            self.rating = reviews.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating'] or 0
            self.reviews_count = reviews.count()
        else:
            self.rating = 0
            self.reviews_count = 0
        
        self.save(update_fields=['rating', 'reviews_count'])


class DealerImage(AbstractBaseModel):
    """
    Дополнительные изображения дилерского центра
    """
    IMAGE_TYPES = [
        ('exterior', _('Внешний вид')),
        ('interior', _('Интерьер')),
        ('office', _('Офис')),
        ('warehouse', _('Склад')),
        ('showroom', _('Выставочный зал')),
        ('team', _('Команда')),
        ('certificate', _('Сертификат')),
        ('other', _('Другое')),
    ]
    
    dealer = models.ForeignKey(
        DealerCenter,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Дилерский центр')
    )
    title = models.CharField(
        _('Название'),
        max_length=200
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='dealers/gallery/'
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
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок'),
        default=0
    )
    
    class Meta:
        verbose_name = _('Изображение дилера')
        verbose_name_plural = _('Изображения дилеров')
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f'{self.dealer.name} - {self.title}'


class DealerReview(AbstractBaseModel):
    """
    Отзывы о дилерских центрах
    """
    dealer = models.ForeignKey(
        DealerCenter,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_('Дилерский центр')
    )
    
    # Информация об авторе отзыва
    author_name = models.CharField(
        _('Имя автора'),
        max_length=100
    )
    author_email = models.EmailField(
        _('Email автора'),
        blank=True
    )
    author_phone = models.CharField(
        _('Телефон автора'),
        max_length=20,
        blank=True
    )
    
    # Содержание отзыва
    title = models.CharField(
        _('Заголовок'),
        max_length=200
    )
    content = models.TextField(
        _('Текст отзыва')
    )
    rating = models.PositiveIntegerField(
        _('Оценка'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    
    # Критерии оценки
    service_rating = models.PositiveIntegerField(
        _('Качество обслуживания'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    price_rating = models.PositiveIntegerField(
        _('Цены'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    delivery_rating = models.PositiveIntegerField(
        _('Доставка'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        blank=True,
        null=True
    )
    
    # Рекомендации
    would_recommend = models.BooleanField(
        _('Рекомендует'),
        default=True
    )
    
    # Модерация
    is_approved = models.BooleanField(
        _('Одобрен'),
        default=False
    )
    is_verified = models.BooleanField(
        _('Проверенный отзыв'),
        default=False,
        help_text=_('Отзыв от проверенного покупателя')
    )
    moderated_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Модератор')
    )
    moderated_at = models.DateTimeField(
        _('Дата модерации'),
        blank=True,
        null=True
    )
    
    # Ответ дилера
    dealer_response = models.TextField(
        _('Ответ дилера'),
        blank=True
    )
    dealer_response_date = models.DateTimeField(
        _('Дата ответа дилера'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Отзыв о дилере')
        verbose_name_plural = _('Отзывы о дилерах')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['dealer', 'is_approved']),
            models.Index(fields=['rating', 'created_at']),
        ]
    
    def __str__(self):
        return f'{self.author_name} - {self.dealer.name} ({self.rating}/5)'
    
    def save(self, *args, **kwargs):
        # Обновляем рейтинг дилера при изменении отзыва
        super().save(*args, **kwargs)
        if self.is_approved:
            self.dealer.update_rating()


class DealerContact(AbstractBaseModel):
    """
    Дополнительные контакты дилерского центра
    """
    CONTACT_TYPES = [
        ('sales', _('Отдел продаж')),
        ('service', _('Сервисный центр')),
        ('support', _('Техподдержка')),
        ('accounting', _('Бухгалтерия')),
        ('management', _('Руководство')),
        ('other', _('Другое')),
    ]
    
    dealer = models.ForeignKey(
        DealerCenter,
        on_delete=models.CASCADE,
        related_name='contacts',
        verbose_name=_('Дилерский центр')
    )
    contact_type = models.CharField(
        _('Тип контакта'),
        max_length=20,
        choices=CONTACT_TYPES,
        default='other'
    )
    department = models.CharField(
        _('Отдел'),
        max_length=100
    )
    contact_person = models.CharField(
        _('Контактное лицо'),
        max_length=100,
        blank=True
    )
    phone = models.CharField(
        _('Телефон'),
        max_length=20
    )
    email = models.EmailField(
        _('Email'),
        blank=True
    )
    working_hours = models.CharField(
        _('Режим работы'),
        max_length=200,
        blank=True
    )
    notes = models.TextField(
        _('Примечания'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('Контакт дилера')
        verbose_name_plural = _('Контакты дилеров')
        ordering = ['contact_type', 'department']
    
    def __str__(self):
        return f'{self.dealer.name} - {self.department}'