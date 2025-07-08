from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from apps.core.models import AbstractBaseModel
from django.urls import reverse
import urllib.parse

class DealerCenterManager(models.Manager):
    """Менеджер для модели DealerCenter"""
    
    def active(self):
        """Активные дилерские центры"""
        return self.filter(is_active=True)
    
    def by_region(self, region):
        """Дилеры по региону"""
        return self.active().filter(region=region)
    
    def featured(self):
        """Рекомендуемые дилеры"""
        return self.active().filter(is_featured=True)
    
    def factories(self):
        """Заводы"""
        return self.active().filter(dealer_type='factory')
    
    def dealers_only(self):
        """Только дилеры (без заводов)"""
        return self.active().exclude(dealer_type='factory')


class DealerCenter(AbstractBaseModel):
    """
    Модель дилерского центра
    """
    DEALER_TYPES = [
        ('factory', _('Главный завод')),
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
        default='official'
    )
    dealer_code = models.CharField(
        _('Код дилера'),
        max_length=20,
        unique=True,
        blank=True
    )
    
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
    
    working_hours = models.TextField(
        _('Режим работы'),
        default='Пн-Пт: 9:00-18:00\nСб: 9:00-15:00\nВс: выходной'
    )
    
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    
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
        default=0,
        help_text=_('Чем меньше число, тем выше в списке. Заводы всегда показываются первыми.')
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
        if not self.dealer_code:
            self.dealer_code = self.generate_dealer_code()
        
        if self.dealer_type == 'factory':
            self.is_featured = True
            if self.sort_order == 0:
                self.sort_order = 1  
        
        super().save(*args, **kwargs)
    
    def generate_dealer_code(self):
        """Генерирует уникальный код дилера"""
        import random
        import string
        
        if self.dealer_type == 'factory':
            prefix = 'FAC'
        else:
            region_code = self.region[:2].upper()
            city_code = self.city[:2].upper()
            prefix = f'{region_code}{city_code}'
        
        for i in range(1, 1000):
            code = f'{prefix}{i:03d}'
            if not DealerCenter.objects.filter(dealer_code=code).exists():
                return code
        
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
        return f'{prefix}{random_part}'
    
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
    def yandex_maps_url(self):
        """Генерирует ссылку на Яндекс карты"""
        if self.has_coordinates:
            return f"https://yandex.by/maps/?pt={self.longitude},{self.latitude}&z=16&l=map"
        else:
            search_query = f"{self.city}, {self.address}"
            encoded_query = urllib.parse.quote(search_query)
            return f"https://yandex.by/maps/?text={encoded_query}"
    
    @property
    def region_display(self):
        """Отображение региона"""
        return dict(self.REGIONS).get(self.region, self.region)
    
    @property
    def dealer_type_display(self):
        """Отображение типа дилера"""
        return dict(self.DEALER_TYPES).get(self.dealer_type, self.dealer_type)
    
    @property
    def is_factory(self):
        """Проверяет, является ли объект заводом"""
        return self.dealer_type == 'factory'
    
    def get_absolute_url(self):
        """Абсолютный URL дилера"""
        return reverse('dealers:dealer_detail', kwargs={'pk': self.pk})