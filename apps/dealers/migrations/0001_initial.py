# Generated by Django 4.2.16 on 2025-06-29 11:41

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="DealerCenter",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Отметьте, чтобы объект был активным",
                        verbose_name="Активный",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="Название")),
                (
                    "full_name",
                    models.CharField(
                        blank=True, max_length=500, verbose_name="Полное название"
                    ),
                ),
                (
                    "dealer_type",
                    models.CharField(
                        choices=[
                            ("official", "Официальный дилер"),
                            ("authorized", "Авторизованный дилер"),
                            ("partner", "Партнер"),
                            ("distributor", "Дистрибьютор"),
                        ],
                        default="partner",
                        max_length=20,
                        verbose_name="Тип дилера",
                    ),
                ),
                (
                    "dealer_code",
                    models.CharField(
                        blank=True,
                        max_length=20,
                        unique=True,
                        verbose_name="Код дилера",
                    ),
                ),
                (
                    "contact_person",
                    models.CharField(max_length=100, verbose_name="Контактное лицо"),
                ),
                (
                    "position",
                    models.CharField(
                        blank=True, max_length=100, verbose_name="Должность"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        max_length=13,
                        validators=[
                            django.core.validators.RegexValidator(
                                message='Номер телефона должен быть в формате: "+375XXXXXXXXX"',
                                regex="^\\+?375\\d{9}$",
                            )
                        ],
                        verbose_name="Телефон",
                    ),
                ),
                ("email", models.EmailField(max_length=254, verbose_name="Email")),
                ("website", models.URLField(blank=True, verbose_name="Веб-сайт")),
                (
                    "region",
                    models.CharField(
                        choices=[
                            ("minsk", "Минская область"),
                            ("gomel", "Гомельская область"),
                            ("brest", "Брестская область"),
                            ("vitebsk", "Витебская область"),
                            ("grodno", "Гродненская область"),
                            ("mogilev", "Могилевская область"),
                            ("minsk_city", "г. Минск"),
                        ],
                        max_length=20,
                        verbose_name="Область",
                    ),
                ),
                ("city", models.CharField(max_length=50, verbose_name="Город")),
                ("address", models.TextField(verbose_name="Адрес")),
                (
                    "postal_code",
                    models.CharField(
                        blank=True, max_length=10, verbose_name="Почтовый индекс"
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=8,
                        max_digits=10,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-90),
                            django.core.validators.MaxValueValidator(90),
                        ],
                        verbose_name="Широта",
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=8,
                        max_digits=11,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-180),
                            django.core.validators.MaxValueValidator(180),
                        ],
                        verbose_name="Долгота",
                    ),
                ),
                (
                    "working_hours",
                    models.TextField(
                        default="Пн-Пт: 9:00-18:00\nСб: 9:00-15:00\nВс: выходной",
                        verbose_name="Режим работы",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                (
                    "is_featured",
                    models.BooleanField(
                        default=False,
                        help_text="Отображать в топе списка",
                        verbose_name="Рекомендуемый",
                    ),
                ),
                (
                    "is_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Дилер прошел проверку",
                        verbose_name="Проверенный",
                    ),
                ),
                (
                    "sort_order",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Порядок сортировки"
                    ),
                ),
            ],
            options={
                "verbose_name": "Дилерский центр",
                "verbose_name_plural": "Дилерские центры",
                "ordering": ["sort_order", "region", "city", "name"],
                "indexes": [
                    models.Index(
                        fields=["region", "city"], name="dealers_dea_region_4702bf_idx"
                    ),
                    models.Index(
                        fields=["dealer_type", "is_active"],
                        name="dealers_dea_dealer__36c47b_idx",
                    ),
                    models.Index(
                        fields=["is_featured", "is_active"],
                        name="dealers_dea_is_feat_a1f0e0_idx",
                    ),
                ],
            },
        ),
    ]
