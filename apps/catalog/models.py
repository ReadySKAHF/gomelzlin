from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from apps.core.models import AbstractBaseModel, SeoModel


class Category(AbstractBaseModel, SeoModel):
    """
    Модель категории товаров
    """
    name = models.CharField(
        _('Название'),
        max_length=100
    )
    slug = models.SlugField(
        _('URL'),
        max_length=100,
        unique=True,
        help_text=_('Уникальный URL для категории')
    )
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительская категория')
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='categories/',
        blank=True,
        null=True
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0
    )
    is_featured = models.BooleanField(
        _('Рекомендуемая'),
        default=False,
        help_text=_('Отображать на главной странице')
    )
    
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})


class ProductManager(models.Manager):
    """Менеджер для модели Product"""
    
    def active(self):
        """Возвращает только активные товары"""
        return self.filter(is_active=True, is_published=True)
    
    def in_stock(self):
        """Возвращает товары в наличии"""
        return self.active().filter(stock_quantity__gt=0)
    
    def featured(self):
        """Возвращает рекомендуемые товары"""
        return self.active().filter(is_featured=True)


class Product(AbstractBaseModel, SeoModel):
    """
    Модель товара
    """
    UNITS = [
        ('pcs', _('шт')),
        ('kg', _('кг')),
        ('m', _('м')),
        ('m2', _('м²')),
        ('m3', _('м³')),
        ('l', _('л')),
        ('set', _('комплект')),
    ]
    
    STATUS_CHOICES = [
        ('draft', _('Черновик')),
        ('published', _('Опубликован')),
        ('archived', _('Архивный')),
    ]
    
    # Основная информация
    name = models.CharField(
        _('Название'),
        max_length=255
    )
    slug = models.SlugField(
        _('URL'),
        max_length=255,
        unique=True
    )
    article = models.CharField(
        _('Артикул'),
        max_length=50,
        unique=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name=_('Категория')
    )
    
    # Описание
    short_description = models.TextField(
        _('Краткое описание'),
        max_length=500,
        blank=True
    )
    description = models.TextField(
        _('Подробное описание'),
        blank=True
    )
    specifications = models.TextField(
        _('Технические характеристики'),
        blank=True,
        help_text=_('Каждая характеристика с новой строки в формате "Название: Значение"')
    )
    
    # Цена и наличие
    price = models.DecimalField(
        _('Цена'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    old_price = models.DecimalField(
        _('Старая цена'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)],
        help_text=_('Для отображения скидки')
    )
    
    # Склад
    stock_quantity = models.PositiveIntegerField(
        _('Количество на складе'),
        default=0
    )
    min_stock_level = models.PositiveIntegerField(
        _('Минимальный остаток'),
        default=5,
        help_text=_('Уровень для предупреждения о низком остатке')
    )
    unit = models.CharField(
        _('Единица измерения'),
        max_length=10,
        choices=UNITS,
        default='pcs'
    )
    
    # Характеристики товара
    weight = models.DecimalField(
        _('Вес (кг)'),
        max_digits=8,
        decimal_places=3,
        blank=True,
        null=True
    )
    dimensions = models.CharField(
        _('Размеры (ДxШxВ)'),
        max_length=100,
        blank=True,
        help_text=_('Размеры в мм')
    )
    material = models.CharField(
        _('Материал'),
        max_length=100,
        blank=True
    )
    color = models.CharField(
        _('Цвет'),
        max_length=50,
        blank=True
    )
    
    # Статус и настройки
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    is_published = models.BooleanField(
        _('Опубликован'),
        default=False
    )
    is_featured = models.BooleanField(
        _('Рекомендуемый'),
        default=False
    )
    is_bestseller = models.BooleanField(
        _('Хит продаж'),
        default=False
    )
    is_new = models.BooleanField(
        _('Новинка'),
        default=False
    )
    
    # Метрики
    views_count = models.PositiveIntegerField(
        _('Количество просмотров'),
        default=0
    )
    orders_count = models.PositiveIntegerField(
        _('Количество заказов'),
        default=0
    )
    
    # Даты
    published_at = models.DateTimeField(
        _('Дата публикации'),
        blank=True,
        null=True
    )
    
    objects = ProductManager()
    
    class Meta:
        verbose_name = _('Товар')
        verbose_name_plural = _('Товары')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_active', 'is_published']),
            models.Index(fields=['article']),
            models.Index(fields=['price']),
            models.Index(fields=['stock_quantity']),
            models.Index(fields=['is_featured', 'is_published']),
        ]
    
    def __str__(self):
        return f'{self.name} ({self.article})'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.name}-{self.article}')
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})
    
    @property
    def is_in_stock(self):
        """Проверяет наличие товара на складе"""
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        """Проверяет низкий остаток товара"""
        return self.stock_quantity <= self.min_stock_level
    
    @property
    def discount_percentage(self):
        """Рассчитывает процент скидки"""
        if self.old_price and self.old_price > self.price:
            return round(((self.old_price - self.price) / self.old_price) * 100)
        return 0
    
    @property
    def has_discount(self):
        """Проверяет наличие скидки"""
        return self.discount_percentage > 0
    
    def get_specifications_dict(self):
        """Преобразует характеристики в словарь"""
        if not self.specifications:
            return {}
        
        specs = {}
        for line in self.specifications.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                specs[key.strip()] = value.strip()
        return specs
    
    def increment_views(self):
        """Увеличивает счетчик просмотров"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class ProductImage(AbstractBaseModel):
    """
    Изображения товаров
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name=_('Товар')
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='products/'
    )
    alt_text = models.CharField(
        _('Альтернативный текст'),
        max_length=255,
        blank=True
    )
    is_main = models.BooleanField(
        _('Главное изображение'),
        default=False
    )
    sort_order = models.PositiveIntegerField(
        _('Порядок'),
        default=0
    )
    
    class Meta:
        verbose_name = _('Изображение товара')
        verbose_name_plural = _('Изображения товаров')
        ordering = ['sort_order', 'created_at']
    
    def __str__(self):
        return f'Изображение для {self.product.name}'