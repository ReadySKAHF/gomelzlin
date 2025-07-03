from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Например: "Офис", "Склад", "Дом"', max_length=100, verbose_name='Название адреса')),
                ('country', models.CharField(default='Беларусь', max_length=50, verbose_name='Страна')),
                ('city', models.CharField(max_length=50, verbose_name='Город')),
                ('address', models.TextField(help_text='Улица, дом, квартира/офис', verbose_name='Полный адрес')),
                ('postal_code', models.CharField(blank=True, max_length=10, verbose_name='Почтовый индекс')),
                ('contact_person', models.CharField(blank=True, help_text='Кто будет принимать заказ по этому адресу', max_length=100, verbose_name='Контактное лицо')),
                ('contact_phone', models.CharField(blank=True, max_length=13, verbose_name='Телефон контактного лица')),
                ('notes', models.TextField(blank=True, help_text='Дополнительная информация для курьера (этаж, код домофона и т.д.)', verbose_name='Примечания')),
                ('is_default', models.BooleanField(default=False, verbose_name='Адрес по умолчанию')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_addresses', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Адрес доставки',
                'verbose_name_plural': 'Адреса доставки',
                'ordering': ['-is_default', '-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='deliveryaddress',
            constraint=models.UniqueConstraint(condition=models.Q(('is_default', True)), fields=('user',), name='unique_default_address_per_user'),
        ),
    ]