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
            # Сначала проверяем, существует ли категория
            category = Category.objects.filter(name=category_name).first()
            
            if not category:
                # Создаем новую категорию только если её нет
                category = Category.objects.create(
                    name=category_name,
                    slug=self.generate_unique_slug(category_name),
                    description=f'Описание категории {category_name}',
                    is_active=True,
                    is_featured=i < 5,  # Первые 5 как рекомендуемые
                    sort_order=i + 1
                )
                self.stdout.write(f'✓ Создана категория: {category_name}')
            else:
                self.stdout.write(f'  Категория уже существует: {category_name}')
            
            created_categories.append(category)
        
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
                    # Проверяем, существует ли подкатегория
                    subcategory = Category.objects.filter(
                        name=subcategory_name, 
                        parent=parent_category
                    ).first()
                    
                    if not subcategory:
                        subcategory = Category.objects.create(
                            name=subcategory_name,
                            parent=parent_category,
                            slug=self.generate_unique_slug(f"{parent_name}-{subcategory_name}"),
                            description=f'Подкатегория {subcategory_name}',
                            is_active=True,
                            sort_order=j + 1
                        )
                        self.stdout.write(f'✓ Создана подкатегория: {subcategory_name}')
                    else:
                        self.stdout.write(f'  Подкатегория уже существует: {subcategory_name}')
                        
            except Category.DoesNotExist:
                self.stdout.write(f'❌ Родительская категория не найдена: {parent_name}')
        
        # Создаем несколько тестовых товаров
        sample_products = [
            ('ЖВН-6А', 'Жатка валковая навесная 6-метровая', 'Зерноуборочная техника', 'Жатки валковые навесные'),
            ('ЖЗК-10', 'Жатка для зерновых культур 10-метровая', 'Зерноуборочная техника', 'Жатки для зерновых культур'),
            ('ПЗ-3', 'Подборщик зерновой 3-метровый', 'Зерноуборочная техника', 'Подборщики зерновые'),
            ('ЖТ-4', 'Жатка для трав 4-метровая', 'Кормоуборочная техника', 'Жатки для трав'),
            ('КУ-7', 'Кормоуборочный комбайн универсальный', 'Кормоуборочная техника', 'Кормоуборочные комбайны'),
        ]
        
        products_created = 0
        for article, name, category_name, subcategory_name in sample_products:
            try:
                category = Category.objects.get(name=subcategory_name, parent__name=category_name)
                
                # Проверяем, существует ли товар
                if not Product.objects.filter(article=article).exists():
                    product = Product.objects.create(
                        name=name,
                        article=article,
                        slug=self.generate_unique_slug(f"{name}-{article}"),
                        description=f'Описание товара {name}',
                        category=category,
                        price=Decimal(str(random.randint(100000, 2000000))),
                        stock_quantity=random.randint(1, 10),
                        is_active=True,
                        is_published=True
                    )
                    products_created += 1
                    self.stdout.write(f'✓ Создан товар: {name} ({article})')
                else:
                    self.stdout.write(f'  Товар уже существует: {article}')
                    
            except Category.DoesNotExist:
                self.stdout.write(f'❌ Категория не найдена: {subcategory_name}')
        
        self.stdout.write(f'\n📊 Статистика:')
        self.stdout.write(f'  Товаров создано: {products_created}')
        self.stdout.write(f'  Всего категорий: {Category.objects.count()}')
        self.stdout.write(f'  Всего товаров: {Product.objects.count()}')
        self.stdout.write('✅ Загрузка данных завершена!')

    def generate_unique_slug(self, text):
        """Генерирует уникальный slug"""
        base_slug = slugify(text)
        slug = base_slug
        counter = 1
        
        while Category.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug