from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from apps.core.models import AbstractBaseModel

User = get_user_model()


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
    
    # Связь с пользователем
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        verbose_name=_('Пользователь'),
        null=True,
        blank=True
    )
    
    # Основная информация
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
    
    # Контактная информация (может отличаться от пользователя)
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
    
    # Адресная информация
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
    
    # Коммерческая информация
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
    
    # Метрики
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
    
    # Дополнительная информация
    source = models.CharField(
        _('Источник'),
        max_length=100,
        blank=True,
        help_text=_('Откуда узнал о компании')
    )
    assigned_manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_customers',
        verbose_name=_('Персональный менеджер'),
        limit_choices_to={'user_type__in': ['admin', 'manager']}
    )
    notes = models.TextField(
        _('Заметки'),
        blank=True
    )
    
    # Настройки уведомлений
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
        else:  # fixed
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
        
        # Автоматическое присвоение VIP статуса
        if self.total_spent >= 50000 or self.total_orders >= 20:
            if self.status != 'vip':
                self.status = 'vip'
        
        self.save(update_fields=[
            'total_orders', 'total_spent', 'average_order_value', 
            'last_order_date', 'status'
        ])


class Organization(AbstractBaseModel):
    """
    Модель организации для юридических лиц
    """
    LEGAL_FORMS = [
        ('OOO', _('ООО')),
        ('OAO', _('ОАО')),
        ('ZAO', _('ЗАО')),
        ('IP', _('ИП')),
        ('UP', _('УП')),
        ('GP', _('ГП')),
        ('OTHER', _('Другое')),
    ]
    
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='organization',
        verbose_name=_('Клиент')
    )
    
    # Основная информация
    full_name = models.CharField(
        _('Полное наименование'),
        max_length=500
    )
    short_name = models.CharField(
        _('Краткое наименование'),
        max_length=255
    )
    legal_form = models.CharField(
        _('Организационно-правовая форма'),
        max_length=10,
        choices=LEGAL_FORMS,
        default='OOO'
    )
    
    # Регистрационные данные
    unp = models.CharField(
        _('УНП'),
        max_length=9,
        unique=True,
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
    registration_date = models.DateField(
        _('Дата регистрации'),
        blank=True,
        null=True
    )
    registration_authority = models.CharField(
        _('Орган регистрации'),
        max_length=255,
        blank=True
    )
    
    # Адреса
    legal_address = models.TextField(
        _('Юридический адрес')
    )
    postal_address = models.TextField(
        _('Почтовый адрес'),
        blank=True
    )
    actual_address = models.TextField(
        _('Фактический адрес'),
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
    bank_address = models.TextField(
        _('Адрес банка'),
        blank=True
    )
    
    # Налоговая информация
    vat_payer = models.BooleanField(
        _('Плательщик НДС'),
        default=True
    )
    vat_number = models.CharField(
        _('Номер плательщика НДС'),
        max_length=20,
        blank=True
    )
    
    # Руководство
    director_name = models.CharField(
        _('ФИО руководителя'),
        max_length=100,
        blank=True
    )
    director_position = models.CharField(
        _('Должность руководителя'),
        max_length=100,
        default='Директор'
    )
    accountant_name = models.CharField(
        _('ФИО главного бухгалтера'),
        max_length=100,
        blank=True
    )
    
    # Дополнительная информация
    activity_codes = models.TextField(
        _('Коды видов деятельности'),
        blank=True,
        help_text=_('Коды ОКЭД через запятую')
    )
    employee_count = models.PositiveIntegerField(
        _('Количество сотрудников'),
        blank=True,
        null=True
    )
    website = models.URLField(
        _('Веб-сайт'),
        blank=True
    )
    
    class Meta:
        verbose_name = _('Организация')
        verbose_name_plural = _('Организации')
        ordering = ['short_name']
    
    def __str__(self):
        return f'{self.get_legal_form_display()} "{self.short_name}"'
    
    @property
    def display_name(self):
        """Отображаемое название организации"""
        return f'{self.get_legal_form_display()} "{self.short_name}"'
    
    def get_legal_address_parts(self):
        """Разбирает юридический адрес на части"""
        # Здесь можно добавить логику парсинга адреса
        return {
            'full_address': self.legal_address,
            'postal_code': '',
            'city': '',
            'street': ''
        }


class CustomerTag(AbstractBaseModel):
    """
    Теги для категоризации клиентов
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
        help_text=_('Цвет в формате HEX')
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
    Привязка тегов к клиентам
    """
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='tag_assignments',
        verbose_name=_('Клиент')
    )
    tag = models.ForeignKey(
        CustomerTag,
        on_delete=models.CASCADE,
        related_name='customer_assignments',
        verbose_name=_('Тег')
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Назначил')
    )
    assigned_at = models.DateTimeField(
        _('Дата назначения'),
        auto_now_add=True
    )
    
    class Meta:
        verbose_name = _('Назначение тега')
        verbose_name_plural = _('Назначения тегов')
        unique_together = ['customer', 'tag']
    
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
        ('praise', _('Благодарность')),
    ]
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name=_('Клиент')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name=_('Автор')
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
    reminder_date = models.DateTimeField(
        _('Напомнить'),
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = _('Заметка о клиенте')
        verbose_name_plural = _('Заметки о клиентах')
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.customer} - {self.title}'