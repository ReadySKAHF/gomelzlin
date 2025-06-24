from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from decimal import Decimal
import uuid
from apps.core.models import AbstractBaseModel
from apps.catalog.models import Product

User = get_user_model()


class OrderManager(models.Manager):
    """Менеджер для модели Order"""
    
    def pending(self):
        """Заказы в ожидании"""
        return self.filter(status='pending')
    
    def confirmed(self):
        """Подтвержденные заказы"""
        return self.filter(status='confirmed')
    
    def paid(self):
        """Оплаченные заказы"""
        return self.filter(status='paid')
    
    def shipped(self):
        """Отправленные заказы"""
        return self.filter(status='shipped')
    
    def completed(self):
        """Завершенные заказы"""
        return self.filter(status='completed')
    
    def for_user(self, user):
        """Заказы пользователя"""
        return self.filter(user=user)


class Order(AbstractBaseModel):
    """
    Модель заказа
    """
    STATUS_CHOICES = [
        ('pending', _('Ожидает обработки')),
        ('confirmed', _('Подтвержден')),
        ('processing', _('В обработке')),
        ('paid', _('Оплачен')),
        ('shipped', _('Отправлен')),
        ('delivered', _('Доставлен')),
        ('completed', _('Завершен')),
        ('cancelled', _('Отменен')),
        ('refunded', _('Возвращен')),
    ]
    
    PAYMENT_METHODS = [
        ('cash', _('Наличный расчет')),
        ('bank_transfer', _('Банковский перевод')),
        ('card', _('Банковская карта')),
        ('invoice', _('По счету')),
    ]
    
    DELIVERY_METHODS = [
        ('pickup', _('Самовывоз')),
        ('delivery', _('Доставка')),
        ('transport_company', _('Транспортная компания')),
    ]
    
    # Основная информация
    number = models.CharField(
        _('Номер заказа'),
        max_length=20,
        unique=True,
        editable=False
    )
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='orders',
        verbose_name=_('Пользователь'),
        null=True,
        blank=True
    )
    session_key = models.CharField(
        _('Ключ сессии'),
        max_length=40,
        blank=True,
        help_text=_('Для анонимных заказов')
    )
    
    # Статус
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Контактная информация
    customer_name = models.CharField(
        _('Имя заказчика'),
        max_length=100
    )
    customer_email = models.EmailField(
        _('Email заказчика')
    )
    customer_phone = models.CharField(
        _('Телефон заказчика'),
        max_length=20
    )
    
    # Информация о компании (для юр. лиц)
    company_name = models.CharField(
        _('Название организации'),
        max_length=255,
        blank=True
    )
    company_unp = models.CharField(
        _('УНП'),
        max_length=9,
        blank=True
    )
    company_address = models.TextField(
        _('Юридический адрес'),
        blank=True
    )
    
    # Доставка
    delivery_method = models.CharField(
        _('Способ доставки'),
        max_length=20,
        choices=DELIVERY_METHODS,
        default='pickup'
    )
    delivery_address = models.TextField(
        _('Адрес доставки'),
        blank=True
    )
    delivery_date = models.DateField(
        _('Дата доставки'),
        blank=True,
        null=True
    )
    delivery_time = models.CharField(
        _('Время доставки'),
        max_length=50,
        blank=True
    )
    delivery_cost = models.DecimalField(
        _('Стоимость доставки'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Оплата
    payment_method = models.CharField(
        _('Способ оплаты'),
        max_length=20,
        choices=PAYMENT_METHODS,
        default='cash'
    )
    is_paid = models.BooleanField(
        _('Оплачен'),
        default=False
    )
    paid_at = models.DateTimeField(
        _('Дата оплаты'),
        blank=True,
        null=True
    )
    
    # Суммы
    subtotal = models.DecimalField(
        _('Сумма товаров'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    discount_amount = models.DecimalField(
        _('Размер скидки'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    tax_amount = models.DecimalField(
        _('Сумма налога'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_amount = models.DecimalField(
        _('Общая сумма'),
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Дополнительная информация
    notes = models.TextField(
        _('Комментарий к заказу'),
        blank=True
    )
    admin_notes = models.TextField(
        _('Внутренние заметки'),
        blank=True
    )
    
    # Метаинформация
    ip_address = models.GenericIPAddressField(
        _('IP-адрес'),
        blank=True,
        null=True
    )
    user_agent = models.TextField(
        _('User Agent'),
        blank=True
    )
    
    objects = OrderManager()
    
    class Meta:
        verbose_name = _('Заказ')
        verbose_name_plural = _('Заказы')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['is_paid', 'status']),
        ]
    
    def __str__(self):
        return f'Заказ №{self.number}'
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Генерирует уникальный номер заказа"""
        import random
        import string
        from django.utils import timezone
        
        # Формат: YYYYMMDD-XXXXX (дата + 5 случайных цифр)
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=5))
        number = f'{date_part}-{random_part}'
        
        # Проверяем уникальность
        while Order.objects.filter(number=number).exists():
            random_part = ''.join(random.choices(string.digits, k=5))
            number = f'{date_part}-{random_part}'
        
        return number
    
    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'number': self.number})
    
    @property
    def items_count(self):
        """Общее количество товаров в заказе"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def is_editable(self):
        """Можно ли редактировать заказ"""
        return self.status in ['pending', 'confirmed']
    
    @property
    def can_be_cancelled(self):
        """Можно ли отменить заказ"""
        return self.status in ['pending', 'confirmed', 'processing']
    
    def calculate_totals(self):
        """Пересчитывает суммы заказа"""
        self.subtotal = sum(
            item.get_total_price() for item in self.items.all()
        )
        self.total_amount = self.subtotal + self.delivery_cost - self.discount_amount + self.tax_amount
        self.save(update_fields=['subtotal', 'total_amount'])
    
    def mark_as_paid(self):
        """Отмечает заказ как оплаченный"""
        from django.utils import timezone
        
        self.is_paid = True
        self.paid_at = timezone.now()
        if self.status == 'pending':
            self.status = 'paid'
        self.save(update_fields=['is_paid', 'paid_at', 'status'])


class OrderItem(models.Model):
    """
    Позиция заказа
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Заказ')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        verbose_name=_('Товар')
    )
    quantity = models.PositiveIntegerField(
        _('Количество'),
        validators=[MinValueValidator(1)]
    )
    price = models.DecimalField(
        _('Цена за единицу'),
        max_digits=10,
        decimal_places=2
    )
    
    # Сохраняем информацию о товаре на момент заказа
    product_name = models.CharField(
        _('Название товара'),
        max_length=255
    )
    product_article = models.CharField(
        _('Артикул'),
        max_length=50
    )
    
    class Meta:
        verbose_name = _('Позиция заказа')
        verbose_name_plural = _('Позиции заказа')
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
    
    def save(self, *args, **kwargs):
        # Сохраняем информацию о товаре
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_article:
            self.product_article = self.product.article
        if not self.price:
            self.price = self.product.price
        super().save(*args, **kwargs)
    
    def get_total_price(self):
        """Общая стоимость позиции"""
        return self.price * self.quantity


class Cart(models.Model):
    """
    Корзина покупок
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name=_('Пользователь'),
        null=True,
        blank=True
    )
    session_key = models.CharField(
        _('Ключ сессии'),
        max_length=40,
        blank=True
    )
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True
    )
    
    class Meta:
        verbose_name = _('Корзина')
        verbose_name_plural = _('Корзины')
        unique_together = ['user', 'session_key']
    
    def __str__(self):
        if self.user:
            return f'Корзина {self.user.email}'
        return f'Корзина (сессия: {self.session_key})'
    
    @property
    def items_count(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def total_price(self):
        """Общая стоимость корзины"""
        return sum(item.get_total_price() for item in self.items.all())
    
    def add_product(self, product, quantity=1):
        """Добавляет товар в корзину"""
        item, created = self.items.get_or_create(
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return item
    
    def remove_product(self, product):
        """Удаляет товар из корзины"""
        self.items.filter(product=product).delete()
    
    def clear(self):
        """Очищает корзину"""
        self.items.all().delete()


class CartItem(models.Model):
    """
    Элемент корзины
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Корзина')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Товар')
    )
    quantity = models.PositiveIntegerField(
        _('Количество'),
        default=1,
        validators=[MinValueValidator(1)]
    )
    added_at = models.DateTimeField(
        _('Дата добавления'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('Элемент корзины')
        verbose_name_plural = _('Элементы корзины')
        unique_together = ['cart', 'product']
    
    def __str__(self):
        return f'{self.product.name} x {self.quantity}'
    
    def get_total_price(self):
        """Общая стоимость элемента"""
        return self.product.price * self.quantity
    
    def increase_quantity(self, amount=1):
        """Увеличивает количество"""
        self.quantity += amount
        self.save()
    
    def decrease_quantity(self, amount=1):
        """Уменьшает количество"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
        else:
            self.delete()


class OrderStatusHistory(AbstractBaseModel):
    """
    История изменения статуса заказа
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Заказ')
    )
    old_status = models.CharField(
        _('Предыдущий статус'),
        max_length=20,
        choices=Order.STATUS_CHOICES,
        blank=True
    )
    new_status = models.CharField(
        _('Новый статус'),
        max_length=20,
        choices=Order.STATUS_CHOICES
    )
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Изменил')
    )
    comment = models.TextField(
        _('Комментарий'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('История статуса заказа')
        verbose_name_plural = _('История статусов заказов')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.order.number}: {self.old_status} → {self.new_status}'


class Wishlist(AbstractBaseModel):
    """
    Список желаний
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wishlists',
        verbose_name=_('Пользователь')
    )
    name = models.CharField(
        _('Название'),
        max_length=100,
        default='Основной список'
    )
    is_public = models.BooleanField(
        _('Публичный'),
        default=False
    )
    
    class Meta:
        verbose_name = _('Список желаний')
        verbose_name_plural = _('Списки желаний')
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f'{self.user.get_full_name()} - {self.name}'


class WishlistItem(models.Model):
    """
    Элемент списка желаний
    """
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Список желаний')
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name=_('Товар')
    )
    added_at = models.DateTimeField(
        _('Дата добавления'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('Элемент списка желаний')
        verbose_name_plural = _('Элементы списка желаний')
        unique_together = ['wishlist', 'product']
    
    def __str__(self):
        return f'{self.wishlist.name} - {self.product.name}'