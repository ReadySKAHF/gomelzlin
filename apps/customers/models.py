from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.conf import settings
from apps.core.models import AbstractBaseModel


class CustomerManager(models.Manager):
    """Менеджер для модели Customer"""
    
    def active(self):
        """Активные клиенты"""
        return self.filter(is_active=True)
    
    def vip(self):
        """VIP клиенты"""
        return self.filter(status='vip')
    
    def companies(self):
        """Юридические лица"""
        return self.filter(customer_type='company')
    
    def individuals(self):
        """Физические лица"""
        return self.filter(customer_type='individual')


class Customer(AbstractBaseModel):
    """
    Модель клиента (расширенная информация о пользователе для CRM)
    """
    CUSTOMER_TYPES = [
        ('individual', _('Физическое лицо')),
        ('company', _('Юридическое лицо')),
    ]
    
    STATUS_CHOICES = [
        ('new', _('Новый')),
        ('active', _('Активный')),
        ('vip', _('VIP')),
        ('inactive', _('Неактивный')),
        ('blocked', _('Заблокированный')),
    ]
    
    DISCOUNT_TYPES = [
        ('percentage', _('Процент')),
        ('fixed', _('Фиксированная сумма')),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('Пользователь'),
        null=True,
        blank=True
    )

    customer_type = models.CharField(
        _('Тип клиента'),
        max_length=20,
        choices=CUSTOMER_TYPES,
        default='individual'
    )
    status = models.CharField(
        _('Статус'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )

    contact_name = models.CharField(
        _('Контактное лицо'),
        max_length=100
    )
    email = models.EmailField(
        _('Email'),
        unique=True
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

    country = models.CharField(
        _('Страна'),
        max_length=50,
        default='Беларусь'
    )
    region = models.CharField(
        _('Область'),
        max_length=50,
        blank=True
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

    discount_type = models.CharField(
        _('Тип скидки'),
        max_length=20,
        choices=DISCOUNT_TYPES,
        default='percentage'
    )
    discount_value = models.DecimalField(
        _('Размер скидки'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    credit_limit = models.DecimalField(
        _('Кредитный лимит'),
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_('Максимальная сумма задолженности')
    )
    payment_terms = models.PositiveIntegerField(
        _('Срок оплаты (дни)'),
        default=0,
        help_text=_('Количество дней для оплаты счета')
    )

    total_orders = models.PositiveIntegerField(
        _('Всего заказов'),
        default=0
    )
    total_spent = models.DecimalField(
        _('Общая сумма покупок'),
        max_digits=12,
        decimal_places=2,
        default=0
    )
    average_order_value = models.DecimalField(
        _('Средний чек'),
        max_digits=10,
        decimal_places=2,
        default=0
    )
    last_order_date = models.DateTimeField(
        _('Дата последнего заказа'),
        blank=True,
        null=True
    )

    source = models.CharField(
        _('Источник'),
        max_length=100,
        blank=True,
        help_text=_('Откуда узнал о компании')
    )
    assigned_manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_customers',
        verbose_name=_('Персональный менеджер'),
        limit_choices_to={'user_type__in': ['admin', 'manager']}
    )
    internal_notes = models.TextField(
        _('Внутренние заметки'),
        blank=True,
        help_text=_('Внутренние заметки для администрации')
    )

    email_notifications = models.BooleanField(
        _('Email уведомления'),
        default=True
    )
    sms_notifications = models.BooleanField(
        _('SMS уведомления'),
        default=False
    )
    marketing_consent = models.BooleanField(
        _('Согласие на маркетинг'),
        default=False
    )
    
    objects = CustomerManager()
    
    class Meta:
        verbose_name = _('Клиент')
        verbose_name_plural = _('Клиенты')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone']),
            models.Index(fields=['status', 'customer_type']),
            models.Index(fields=['city']),
            models.Index(fields=['assigned_manager']),
        ]
    
    def __str__(self):
        return f'{self.contact_name} ({self.email})'
    
    @property
    def full_address(self):
        """Полный адрес клиента"""
        parts = [self.postal_code, self.city, self.address]
        return ', '.join(filter(None, parts))
    
    @property
    def is_vip(self):
        """Проверяет VIP статус"""
        return self.status == 'vip'
    
    def calculate_discount(self, amount):
        """Рассчитывает скидку для суммы"""
        if self.discount_value <= 0:
            return 0
        
        if self.discount_type == 'percentage':
            return amount * (self.discount_value / 100)
        else: 
            return min(self.discount_value, amount)
    
    def update_metrics(self):
        """Обновляет метрики клиента"""
        from apps.orders.models import Order
        
        orders = Order.objects.filter(customer_email=self.email, status__in=['paid', 'completed'])
        
        self.total_orders = orders.count()
        self.total_spent = sum(order.total_amount for order in orders)
        
        if self.total_orders > 0:
            self.average_order_value = self.total_spent / self.total_orders
            self.last_order_date = orders.latest('created_at').created_at
        
        if self.total_spent >= 50000 or self.total_orders >= 20:
            if self.status != 'vip':
                self.status = 'vip'
        
        self.save(update_fields=[
            'total_orders', 'total_spent', 'average_order_value', 
            'last_order_date', 'status'
        ])


class CustomerTag(AbstractBaseModel):
    """
    Теги для клиентов
    """
    name = models.CharField(
        _('Название'),
        max_length=50,
        unique=True
    )
    color = models.CharField(
        _('Цвет'),
        max_length=7,
        default='#007bff',
        help_text=_('Цвет в формате HEX (#000000)')
    )
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('Тег клиента')
        verbose_name_plural = _('Теги клиентов')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class CustomerTagAssignment(models.Model):
    """
    Связь клиентов с тегами
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name=_('Клиент')
    )
    tag = models.ForeignKey(
        CustomerTag,
        on_delete=models.CASCADE,
        related_name='customers',
        verbose_name=_('Тег')
    )
    assigned_at = models.DateTimeField(
        _('Дата присвоения'),
        auto_now_add=True
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Присвоил')
    )
    
    class Meta:
        unique_together = ['customer', 'tag']
        verbose_name = _('Тег клиента')
        verbose_name_plural = _('Теги клиентов')
    
    def __str__(self):
        return f'{self.customer} - {self.tag}'


class CustomerNote(AbstractBaseModel):
    """
    Заметки о клиентах
    """
    NOTE_TYPES = [
        ('general', _('Общая')),
        ('call', _('Звонок')),
        ('meeting', _('Встреча')),
        ('email', _('Email')),
        ('complaint', _('Жалоба')),
        ('compliment', _('Благодарность')),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='customer_notes',
        verbose_name=_('Клиент')
    )
    note_type = models.CharField(
        _('Тип заметки'),
        max_length=20,
        choices=NOTE_TYPES,
        default='general'
    )
    title = models.CharField(
        _('Заголовок'),
        max_length=200
    )
    content = models.TextField(
        _('Содержание')
    )
    is_important = models.BooleanField(
        _('Важная'),
        default=False
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Автор')
    )
    
    class Meta:
        verbose_name = _('Заметка о клиенте')
        verbose_name_plural = _('Заметки о клиентах')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.customer} - {self.title}'