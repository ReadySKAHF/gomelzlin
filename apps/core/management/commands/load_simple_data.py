# apps/core/management/commands/load_simple_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Загружает упрощенные данные для тестирования'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка упрощенных данных...')
        
        # Создаем основные категории
        categories_data = [
            'Зерноуборочная техника',
            'Кормоуборочная техника', 
            'Картофелеуборочная техника',
            'Метизная продукция',
            'Прочая техника',
            'Бункеры-перегрузчики',
            'Новинки',
            'Прочие товары, работы и услуги',
            'Режущие системы жаток',
            'Самоходные носилки'
        ]
        
        created_categories = []
        
        for i, category_name in enumerate(categories_data):
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': slugify(category_name),
                    'description': f'Описание категории {category_name}',
                    'is_active': True,
                    'is_featured': i < 5,  # Первые 5 как рекомендуемые
                    'sort_order': i + 1
                }
            )
            created_categories.append(category)
            
            if created:
                self.stdout.write(f'✓ Создана категория: {category_name}')
            else:
                self.stdout.write(f'  Категория уже существует: {category_name}')
        
        # Создаем подкатегории для первых двух категорий
        subcategories_data = {
            'Зерноуборочная техника': [
                'Жатки валковые навесные',
                'Жатки для зерновых культур', 
                'Подборщики зерновые'
            ],
            'Кормоуборочная техника': [
                'Жатки для трав',
                'Кормоуборочные комбайны',
                'Косилки'
            ]
        }
        
        for parent_name, subcategory_names in subcategories_data.items():
            try:
                parent_category = Category.objects.get(name=parent_name)
                for j, subcategory_name in enumerate(subcategory_names):
                    subcategory, created = Category.objects.get_or_create(
                        name=subcategory_name,
                        parent=parent_category,
                        defaults={
                            'slug': slugify(f"{parent_name}-{subcategory_name}"),
                            'description': f'Подкатегория {subcategory_name}',
                            'is_active': True,
                            'sort_order': j + 1
                        }
                    )
                    if created:
                        self.stdout.write(f'  ✓ Создана подкатегория: {subcategory_name}')
            except Category.DoesNotExist:
                continue
        
        # Создаем товары для каждой категории
        products_created = 0
        
        for category in Category.objects.all():
            # Создаем 3-5 товаров для каждой категории
            num_products = random.randint(3, 5)
            
            for i in range(num_products):
                article = f"{category.name[:3].upper()}-{category.id:03d}-{i+1:03d}"
                product_name = f"{category.name} {i+1}"
                
                # Проверяем, не существует ли товар
                if Product.objects.filter(article=article).exists():
                    continue
                
                try:
                    product = Product.objects.create(
                        name=product_name,
                        slug=slugify(f"{article}-{product_name}"),
                        article=article,
                        category=category,
                        short_description=f"Краткое описание {product_name}",
                        description=f"Подробное описание товара {product_name}. Производитель: ОАО 'ГЗЛиН'. Гарантия: 12 месяцев.",
                        price=Decimal(str(random.randint(1000, 500000))),
                        stock_quantity=random.randint(0, 50),
                        unit='pcs',
                        is_active=True,
                        is_published=True,
                        is_featured=random.choice([True, False]),
                        views_count=random.randint(0, 100)
                    )
                    products_created += 1
                except Exception as e:
                    self.stdout.write(f'Ошибка создания товара: {e}')
        
        # Статистика
        total_categories = Category.objects.count()
        total_products = Product.objects.count()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Загрузка завершена!')
        )
        self.stdout.write(f'📊 Создано категорий: {total_categories}')
        self.stdout.write(f'📦 Создано товаров: {total_products}')
        self.stdout.write(f'🆕 Новых товаров: {products_created}')