from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
import uuid
from apps.core.models import AbstractBaseModel


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
    
    number = models.CharField(
        _('Номер заказа'),
        max_length=20,
        unique=True,
        editable=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
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
    
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
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
    
    notes = models.TextField(
        _('Комментарий к заказу'),
        blank=True
    )
    admin_notes = models.TextField(
        _('Внутренние заметки'),
        blank=True
    )
    
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
        
        date_part = timezone.now().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=5))
        number = f'GL-{date_part}-{random_part}'
        
        while Order.objects.filter(number=number).exists():
            random_part = ''.join(random.choices(string.digits, k=5))
            number = f'GL-{date_part}-{random_part}'
        
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
    
    def get_status_display_color(self):
        """Возвращает цвет для отображения статуса"""
        colors = {
            'pending': '#ffc107',      # Желтый
            'confirmed': '#17a2b8',    # Голубой
            'processing': '#fd7e14',   # Оранжевый
            'paid': '#28a745',         # Зеленый
            'shipped': '#6f42c1',      # Фиолетовый
            'delivered': '#28a745',    # Зеленый
            'completed': '#28a745',    # Зеленый
            'cancelled': '#dc3545',    # Красный
            'refunded': '#6c757d',     # Серый
        }
        return colors.get(self.status, '#6c757d')


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
        'catalog.Product',
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
    
    product_name = models.CharField(
        _('Название товара'),
        max_length=255
    )
    product_article = models.CharField(
        _('Артикул'),
        max_length=50,
        blank=True
    )
    
    class Meta:
        verbose_name = _('Позиция заказа')
        verbose_name_plural = _('Позиции заказа')
        unique_together = ['order', 'product']
    
    def __str__(self):
        return f'{self.product_name} x {self.quantity}'
    
    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.name
        if not self.product_article:
            self.product_article = getattr(self.product, 'article', '')
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
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name=_('Пользователь'),
        null=True,
        blank=True
    )
    session_key = models.CharField(
        _('Ключ сессии'),
        max_length=40,
        blank=True,
        unique=True,
        null=True
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
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]
    
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
        """Добавляет товар в корзину с улучшенной обработкой ошибок"""
        try:
            if not product:
                raise ValueError("Товар не может быть None")
            
            if not hasattr(product, 'id'):
                raise ValueError("Товар должен иметь ID")
            
            if quantity <= 0:
                raise ValueError("Количество должно быть больше 0")
            
            try:
                item = self.items.get(product=product)
                item.quantity += quantity
                item.save()
                
            except CartItem.DoesNotExist:
                item = CartItem.objects.create(
                    cart=self,
                    product=product,
                    quantity=quantity
                )

            self.save(update_fields=['updated_at'])
            
            return item
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in Cart.add_product: {e}, cart_id={self.id}, product_id={getattr(product, 'id', 'None')}, quantity={quantity}")
            raise
    
    def remove_product(self, product):
        """Удаляет товар из корзины"""
        self.items.filter(product=product).delete()
    
    def clear(self):
        """Очищает корзину"""
        self.items.all().delete()
    
    def update_quantity(self, product, quantity):
        """Обновляет количество товара в корзине"""
        try:
            item = self.items.get(product=product)
            if quantity <= 0:
                item.delete()
                return None
            else:
                item.quantity = quantity
                item.save()
                return item
        except CartItem.DoesNotExist:
            return None


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
        'catalog.Product',
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
        return self
    
    def decrease_quantity(self, amount=1):
        """Уменьшает количество"""
        if self.quantity > amount:
            self.quantity -= amount
            self.save()
            return self
        else:
            self.delete()
            return None


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
        settings.AUTH_USER_MODEL,
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
        settings.AUTH_USER_MODEL,
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
        'catalog.Product',
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

def get_or_create_cart(user=None, session_key=None):
    """Получить или создать корзину для пользователя или сессии"""
    if user and user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    elif session_key:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
        return cart
    return None


def merge_carts(session_cart, user_cart):
    """Объединить корзины при входе пользователя в систему"""
    if not session_cart or not user_cart:
        return user_cart

    for session_item in session_cart.items.all():
        user_item, created = user_cart.items.get_or_create(
            product=session_item.product,
            defaults={'quantity': session_item.quantity}
        )
        
        if not created:
            user_item.quantity += session_item.quantity
            user_item.save()
    
    session_cart.delete()
    
    return user_cart


def create_order_from_cart(cart, order_data):
    """Создать заказ из корзины с правильным сохранением данных"""
    from django.db import transaction
    
    with transaction.atomic():
        order = Order.objects.create(
            user=order_data.get('user'),
            session_key=order_data.get('session_key', ''),
            
            customer_name=order_data.get('customer_name', ''),
            customer_email=order_data.get('customer_email', ''),
            customer_phone=order_data.get('customer_phone', ''),
            
            company_name=order_data.get('company_name', ''),
            company_unp=order_data.get('company_unp', ''),
            company_address=order_data.get('company_address', ''),
            
            delivery_method=order_data.get('delivery_method', 'pickup'),
            delivery_address=order_data.get('delivery_address', ''),
            delivery_date=order_data.get('delivery_date'),
            delivery_time=order_data.get('delivery_time', ''),
            delivery_cost=Decimal(str(order_data.get('delivery_cost', '0.00'))),
            
            payment_method=order_data.get('payment_method', 'cash'),
            
            subtotal=Decimal('0.00'),
            discount_amount=Decimal(str(order_data.get('discount_amount', '0.00'))),
            tax_amount=Decimal(str(order_data.get('tax_amount', '0.00'))),
            total_amount=Decimal('0.00'),
            
            notes=order_data.get('notes', ''),
            admin_notes=order_data.get('admin_notes', ''),
            
            ip_address=order_data.get('ip_address'),
            user_agent=order_data.get('user_agent', ''),
        )
        
        subtotal = Decimal('0.00')
        for cart_item in cart.items.all():
            order_item = OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.name,
                product_article=getattr(cart_item.product, 'article', ''),
                price=cart_item.product.price,
                quantity=cart_item.quantity
            )
            subtotal += order_item.get_total_price()
        
        order.subtotal = subtotal
        order.total_amount = subtotal + order.delivery_cost - order.discount_amount + order.tax_amount
        order.save()
        
        OrderStatusHistory.objects.create(
            order=order,
            new_status=order.status,
            comment='Заказ создан'
        )
        
        cart.clear()
        
        return order


def get_cart_for_request(request):
    """Получить корзину для текущего запроса"""
    if request.user.is_authenticated:
        return get_or_create_cart(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return get_or_create_cart(session_key=session_key)