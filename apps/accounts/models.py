from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator

class UserManager(BaseUserManager):
    """Менеджер для пользовательской модели User"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Создает и сохраняет обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен')
        
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email)  # Устанавливаем username = email
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Создает и сохраняет суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Расширенная модель пользователя
    """
    USER_TYPES = [
        ('individual', _('Физическое лицо')),
        ('company', _('Юридическое лицо')),
        ('admin', _('Администратор')),
        ('manager', _('Менеджер')),
    ]
    
    email = models.EmailField(
        _('Email'),
        unique=True,
        help_text=_('Обязательное поле. Используется для входа в систему.')
    )
    phone_regex = RegexValidator(
        regex=r'^\+?375\d{9}$',
        message=_('Номер телефона должен быть в формате: "+375XXXXXXXXX"')
    )
    phone = models.CharField(
        _('Телефон'),
        validators=[phone_regex],
        max_length=13,
        blank=True
    )
    user_type = models.CharField(
        _('Тип пользователя'),
        max_length=20,
        choices=USER_TYPES,
        default='individual'
    )
    is_verified = models.BooleanField(
        _('Подтвержден'),
        default=False,
        help_text=_('Указывает, что пользователь подтвердил свой email')
    )
    avatar = models.ImageField(
        _('Аватар'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    birth_date = models.DateField(
        _('Дата рождения'),
        blank=True,
        null=True
    )
    
    # Поля для уведомлений
    email_notifications = models.BooleanField(
        _('Email уведомления'),
        default=True,
        help_text=_('Получать уведомления на email')
    )
    sms_notifications = models.BooleanField(
        _('SMS уведомления'),
        default=False,
        help_text=_('Получать SMS уведомления')
    )
    
    # Поля для аналитики
    last_login_ip = models.GenericIPAddressField(
        _('IP последнего входа'),
        blank=True,
        null=True
    )
    login_count = models.PositiveIntegerField(
        _('Количество входов'),
        default=0
    )
    
    # Даты
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = UserManager()  # Используем наш пользовательский менеджер
    
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']
    
    def __str__(self):
        return f'{self.get_full_name()} ({self.email})'
    
    def get_full_name(self):
        """Возвращает полное имя пользователя"""
        full_name = f'{self.first_name} {self.last_name}'.strip()
        return full_name or self.username
    
    def get_short_name(self):
        """Возвращает короткое имя пользователя"""
        return self.first_name or self.username
    
    @property
    def is_company(self):
        """Проверяет, является ли пользователь юридическим лицом"""
        return self.user_type == 'company'
    
    @property
    def is_individual(self):
        """Проверяет, является ли пользователь физическим лицом"""
        return self.user_type == 'individual'
    
    @property
    def is_admin_user(self):
        """Проверяет, является ли пользователь администратором"""
        return self.user_type in ['admin', 'manager'] or self.is_staff

class UserProfile(models.Model):
    """
    Расширенный профиль пользователя
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('Пользователь')
    )
    
    # Персональная информация
    middle_name = models.CharField(
        _('Отчество'),
        max_length=50,
        blank=True
    )
    position = models.CharField(
        _('Должность'),
        max_length=100,
        blank=True
    )
    department = models.CharField(
        _('Отдел'),
        max_length=100,
        blank=True
    )
    
    # Адресная информация
    country = models.CharField(
        _('Страна'),
        max_length=50,
        default='Беларусь'
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
    postal_code = models.CharField(
        _('Почтовый индекс'),
        max_length=10,
        blank=True
    )
    
    # Дополнительные контакты
    additional_phone = models.CharField(
        _('Дополнительный телефон'),
        max_length=13,
        blank=True
    )
    skype = models.CharField(
        _('Skype'),
        max_length=50,
        blank=True
    )
    telegram = models.CharField(
        _('Telegram'),
        max_length=50,
        blank=True
    )
    
    # Настройки профиля
    language = models.CharField(
        _('Язык'),
        max_length=10,
        choices=[
            ('ru', 'Русский'),
            ('en', 'English'),
        ],
        default='ru'
    )
    timezone = models.CharField(
        _('Часовой пояс'),
        max_length=50,
        default='Europe/Minsk'
    )
    
    # Настройки уведомлений
    order_status_notifications = models.BooleanField(
        _('Уведомления о статусе заказа'),
        default=True
    )
    new_products_notifications = models.BooleanField(
        _('Уведомления о новых товарах'),
        default=False
    )
    special_offers_notifications = models.BooleanField(
        _('Уведомления о спецпредложениях'),
        default=True
    )
    
    # Метаинформация
    notes = models.TextField(
        _('Заметки'),
        blank=True,
        help_text=_('Внутренние заметки для администрации')
    )
    
    # Даты
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')
    
    def __str__(self):
        return f'Профиль {self.user.get_full_name()}'
    
    def get_full_address(self):
        """Возвращает полный адрес"""
        address_parts = [
            self.postal_code,
            self.city,
            self.address
        ]
        return ', '.join(filter(None, address_parts))

class CompanyProfile(models.Model):
    """
    Профиль компании для юридических лиц
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='company_profile',
        verbose_name=_('Пользователь')
    )
    
    # Основная информация о компании
    company_name = models.CharField(
        _('Название организации'),
        max_length=255
    )
    legal_form = models.CharField(
        _('Организационно-правовая форма'),
        max_length=50,
        choices=[
            ('OOO', 'ООО'),
            ('OAO', 'ОАО'),
            ('ZAO', 'ЗАО'),
            ('IP', 'ИП'),
            ('UP', 'УП'),
            ('OTHER', 'Другое'),
        ],
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
    
    # Контактная информация
    legal_address = models.TextField(
        _('Юридический адрес')
    )
    postal_address = models.TextField(
        _('Почтовый адрес'),
        blank=True
    )
    website = models.URLField(
        _('Веб-сайт'),
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
    
    # Дополнительная информация
    activity_type = models.CharField(
        _('Вид деятельности'),
        max_length=255,
        blank=True
    )
    employee_count = models.PositiveIntegerField(
        _('Количество сотрудников'),
        blank=True,
        null=True
    )
    annual_revenue = models.DecimalField(
        _('Годовой оборот'),
        max_digits=15,
        decimal_places=2,
        blank=True,
        null=True
    )
    
    # Контактное лицо компании
    contact_person = models.CharField(
        _('Контактное лицо'),
        max_length=100,
        blank=True
    )
    contact_phone = models.CharField(
        _('Контактный телефон'),
        max_length=13,
        blank=True
    )
    contact_email = models.EmailField(
        _('Контактный email'),
        blank=True
    )
    
    # Заметки
    notes = models.TextField(
        _('Заметки'),
        blank=True,
        help_text=_('Внутренние заметки для администрации')
    )
    
    # Даты
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Профиль компании')
        verbose_name_plural = _('Профили компаний')
    
    def __str__(self):
        return f'{self.company_name} (УНП: {self.unp})'
    
    @property
    def full_company_name(self):
        """Возвращает полное название компании с организационно-правовой формой"""
        return f'{self.get_legal_form_display()} "{self.company_name}"'
    
class DeliveryAddress(models.Model):
    """
    Адреса доставки пользователя
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_addresses',
        verbose_name=_('Пользователь')
    )
    
    # Основная информация об адресе
    title = models.CharField(
        _('Название адреса'),
        max_length=100,
        help_text=_('Например: "Офис", "Склад", "Дом"')
    )
    
    # Адресная информация
    country = models.CharField(
        _('Страна'),
        max_length=50,
        default='Беларусь'
    )
    city = models.CharField(
        _('Город'),
        max_length=50
    )
    address = models.TextField(
        _('Полный адрес'),
        help_text=_('Улица, дом, квартира/офис')
    )
    postal_code = models.CharField(
        _('Почтовый индекс'),
        max_length=10,
        blank=True
    )
    
    # Контактная информация для доставки
    contact_person = models.CharField(
        _('Контактное лицо'),
        max_length=100,
        blank=True,
        help_text=_('Кто будет принимать заказ по этому адресу')
    )
    contact_phone = models.CharField(
        _('Телефон контактного лица'),
        max_length=13,
        blank=True
    )
    
    # Дополнительная информация
    notes = models.TextField(
        _('Примечания'),
        blank=True,
        help_text=_('Дополнительная информация для курьера (этаж, код домофона и т.д.)')
    )
    
    # Настройки
    is_default = models.BooleanField(
        _('Адрес по умолчанию'),
        default=False
    )
    is_active = models.BooleanField(
        _('Активен'),
        default=True
    )
    
    # Даты
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    class Meta:
        verbose_name = _('Адрес доставки')
        verbose_name_plural = _('Адреса доставки')
        ordering = ['-is_default', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(is_default=True),
                name='unique_default_address_per_user'
            )
        ]
    
    def __str__(self):
        return f'{self.title} - {self.city}, {self.address[:50]}'
    
    def save(self, *args, **kwargs):
        # Если это адрес по умолчанию, убираем флаг у других адресов пользователя
        if self.is_default:
            DeliveryAddress.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    def get_full_address(self):
        """Возвращает полный адрес"""
        address_parts = [
            self.postal_code,
            self.city,
            self.address
        ]
        return ', '.join(filter(None, address_parts))
    
    def get_short_address(self):
        """Возвращает краткий адрес для отображения в списках"""
        return f'{self.city}, {self.address[:30]}{"..." if len(self.address) > 30 else ""}'