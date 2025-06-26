from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from apps.core.models import AbstractBaseModel, SeoModel


class CategoryManager(models.Manager):
    """Менеджер для модели Category"""
    
    def active(self):
        """Возвращает только активные категории"""
        return self.filter(is_active=True)
    
    def main_categories(self):
        """Возвращает основные категории (без родителя)"""
        return self.filter(parent__isnull=True, is_active=True)
    
    def featured(self):
        """Возвращает рекомендуемые категории"""
        return self.filter(is_featured=True, is_active=True)

class Category(AbstractBaseModel, SeoModel):
    """
    Модель категории товаров
    """
    name = models.CharField(_('Название'), max_length=255)
    slug = models.SlugField(
        _('URL'), 
        max_length=100, 
        unique=True,
        help_text=_('Уникальный URL для категории')
    )
    description = models.TextField(_('Описание'), blank=True)
    
    # Изображение категории
    image = models.ImageField(
        _('Изображение'),
        upload_to='categories/',
        blank=True,
        null=True,
        help_text=_('Изображение категории для каталога')
    )
    
    # Иерархия категорий
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name=_('Родительская категория'),
        blank=True,
        null=True
    )
    
    # Настройки отображения
    sort_order = models.PositiveIntegerField(
        _('Порядок сортировки'),
        default=0,
        help_text=_('Чем меньше число, тем выше в списке')
    )
    
    is_featured = models.BooleanField(
        _('Рекомендуемая'),
        default=False,
        help_text=_('Отображать на главной странице')
    )
    
    # Менеджер
    objects = CategoryManager()
    
    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['sort_order', 'name']
        indexes = [
            models.Index(fields=['parent', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['sort_order']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        # Автогенерация slug, если не задан
        if not self.slug:
            base_slug = slugify(self.name) if self.name else 'category'
            slug = base_slug
            counter = 1
            
            while Category.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            self.slug = slug
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Возвращает URL категории"""
        if not self.slug:
            return '#'
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})
    
    def get_products_count(self):
        """Возвращает количество товаров в категории"""
        from .models import Product  # Избегаем циклического импорта
        
        count = self.products.filter(is_active=True, is_published=True).count()
        
        # Добавляем товары из подкатегорий
        for child in self.children.filter(is_active=True):
            count += child.products.filter(is_active=True, is_published=True).count()
        
        return count
    
    def get_all_products(self):
        """Возвращает все товары категории включая подкатегории"""
        from .models import Product  # Избегаем циклического импорта
        
        # Если есть подкатегории, возвращаем товары из подкатегорий
        if self.children.filter(is_active=True).exists():
            product_ids = []
            for child in self.children.filter(is_active=True):
                product_ids.extend(
                    child.products.filter(is_active=True, is_published=True).values_list('id', flat=True)
                )
            return Product.objects.filter(id__in=product_ids)
        else:
            # Если подкатегорий нет, возвращаем товары самой категории
            return self.products.filter(is_active=True, is_published=True)
    
    def get_breadcrumbs(self):
        """Возвращает хлебные крошки"""
        breadcrumbs = []
        current = self
        
        while current:
            breadcrumbs.insert(0, {
                'name': current.name,
                'url': current.get_absolute_url()
            })
            current = current.parent
        
        return breadcrumbs
    
    @property
    def has_children(self):
        """Проверяет наличие подкатегорий"""
        return self.children.filter(is_active=True).exists()
    
    @property
    def level(self):
        """Возвращает уровень вложенности категории"""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level

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
    name = models.CharField(_('Название'), max_length=255)
    slug = models.SlugField(_('URL'), max_length=255, unique=True)
    article = models.CharField(_('Артикул'), max_length=50, unique=True)
    category = models.ForeignKey(
        'Category',
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
    description = models.TextField(_('Подробное описание'), blank=True)
    specifications = models.TextField(_('Технические характеристики'), blank=True)
    
    # Цена и наличие
    price = models.DecimalField(
        _('Цена'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    old_price = models.DecimalField(
        _('Старая цена'),
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Склад
    stock_quantity = models.PositiveIntegerField(
        _('Количество на складе'),
        default=0
    )
    min_stock_level = models.PositiveIntegerField(
        _('Минимальный остаток'),
        default=5
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
    
    # Изображение (опционально)
    image = models.ImageField(
        _('Изображение'),
        upload_to='products/',
        blank=True,
        null=True
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