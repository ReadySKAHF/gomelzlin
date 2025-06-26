# apps/core/management/commands/load_initial_data.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Загружает полную структуру категорий, подкатегорий и товаров для ОАО "ГЗЛиН"'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Загрузка категорий, подкатегорий и товаров ОАО "ГЗЛиН"...')
        
        # Полная структура категорий согласно техническому заданию
        categories_data = {
            'Зерноуборочная техника': [
                'Жатки валковые навесные',
                'Жатки валковые прицепные',
                'Жатки для зерновых культур',
                'Жатки для уборки подсолнечника',
                'Жатки для уборки сои и зерновых культур',
                'Жатки транспортные',
                'Комплект оборудования для уборки кукурузы на зерно',
                'Подборщики зерновые'
            ],
            'Кормоуборочная техника': [
                'Жатки для грубостебельных культур',
                'Жатки для трав',
                'Кормоуборочные комбайны',
                'Косилки',
                'Подборщики',
                'Самоходный кормоуборочный комбайн'
            ],
            'Картофелеуборочная техника': [],
            'Метизная продукция': [
                'Болты',
                'Винты',
                'Гайки',
                'Заклепки',
                'Оси',
                'Шайбы пружинные',
                'Шпилька'
            ],
            'Прочая техника': [],
            'Бункеры-перегрузчики': [],
            'Новинки': [],
            'Прочие товары, работы и услуги': [],
            'Режущие системы жаток': [],
            'Самоходные носилки': []
        }
        
        # Описания категорий
        category_descriptions = {
            'Зерноуборочная техника': 'Широкий ассортимент жаток и оборудования для уборки зерновых культур',
            'Кормоуборочная техника': 'Техника для заготовки кормов, жатки для трав и кормоуборочные комбайны',
            'Картофелеуборочная техника': 'Специализированное оборудование для уборки картофеля',
            'Метизная продукция': 'Крепежные изделия, болты, винты, гайки и другие метизы',
            'Прочая техника': 'Дополнительное сельскохозяйственное оборудование',
            'Бункеры-перегрузчики': 'Бункеры и перегрузочное оборудование для зерна',
            'Новинки': 'Новые разработки и инновационные решения ОАО "ГЗЛиН"',
            'Прочие товары, работы и услуги': 'Дополнительные товары и услуги компании',
            'Режущие системы жаток': 'Ножи, сегменты и другие элементы режущих систем',
            'Самоходные носилки': 'Самоходные носилки и транспортное оборудование'
        }
        
        created_categories = 0
        created_subcategories = 0
        created_products = 0
        
        # Создаем категории и подкатегории
        for category_name, subcategories in categories_data.items():
            # Создаем основную категорию
            main_category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': self.generate_unique_slug(category_name),
                    'description': category_descriptions.get(category_name, f'Категория {category_name}'),
                    'is_active': True,
                    'is_featured': True,
                    'sort_order': list(categories_data.keys()).index(category_name) + 1
                }
            )
            
            if created:
                created_categories += 1
                self.stdout.write(f'✓ Создана категория: {category_name}')
            else:
                self.stdout.write(f'  Категория уже существует: {category_name}')
            
            # Создаем подкатегории
            for i, subcategory_name in enumerate(subcategories):
                sub_category, sub_created = Category.objects.get_or_create(
                    name=subcategory_name,
                    parent=main_category,
                    defaults={
                        'slug': self.generate_unique_slug(subcategory_name),
                        'description': f'Подкатегория {subcategory_name}',
                        'is_active': True,
                        'is_featured': False,
                        'sort_order': i + 1
                    }
                )
                
                if sub_created:
                    created_subcategories += 1
                    self.stdout.write(f'  ↳ Создана подкатегория: {subcategory_name}')
                else:
                    self.stdout.write(f'    Подкатегория уже существует: {subcategory_name}')
        
        # Создаем образцы товаров
        sample_products = [
            # Зерноуборочная техника
            ('ЖВН-3', 'Жатка валковая навесная 3-метровая', 'Зерноуборочная техника', 'Жатки валковые навесные'),
            ('ЖВП-4', 'Жатка валковая прицепная 4-метровая', 'Зерноуборочная техника', 'Жатки валковые прицепные'),
            ('ЖЗК-5', 'Жатка для зерновых культур 5-метровая', 'Зерноуборочная техника', 'Жатки для зерновых культур'),
            ('ЖУП-6', 'Жатка для уборки подсолнечника 6-рядная', 'Зерноуборочная техника', 'Жатки для уборки подсолнечника'),
            ('ЖСЗ-4', 'Жатка для сои и зерновых 4-метровая', 'Зерноуборочная техника', 'Жатки для уборки сои и зерновых культур'),
            ('ЖТ-5', 'Жатка транспортная 5-метровая', 'Зерноуборочная техника', 'Жатки транспортные'),
            ('КУК-8', 'Комплект для уборки кукурузы 8-рядный', 'Зерноуборочная техника', 'Комплект оборудования для уборки кукурузы на зерно'),
            ('ПЗ-3', 'Подборщик зерновой 3-метровый', 'Зерноуборочная техника', 'Подборщики зерновые'),
            
            # Кормоуборочная техника
            ('ЖГК-4', 'Жатка для грубостебельных культур 4-метровая', 'Кормоуборочная техника', 'Жатки для грубостебельных культур'),
            ('ЖТР-3', 'Жатка для трав 3-метровая', 'Кормоуборочная техника', 'Жатки для трав'),
            ('КУ-700', 'Кормоуборочный комбайн универсальный', 'Кормоуборочная техника', 'Кормоуборочные комбайны'),
            ('КС-2', 'Косилка сегментная 2-метровая', 'Кормоуборочная техника', 'Косилки'),
            ('ПК-4', 'Подборщик кормов 4-метровый', 'Кормоуборочная техника', 'Подборщики'),
            ('СКК-500', 'Самоходный кормоуборочный комбайн', 'Кормоуборочная техника', 'Самоходный кормоуборочный комбайн'),
            
            # Картофелеуборочная техника (прямо в категории)
            ('КУТ-2', 'Картофелеуборочная техника 2-рядная', 'Картофелеуборочная техника', None),
            ('КК-1', 'Картофелекопалка однорядная', 'Картофелеуборочная техника', None),
            
            # Метизная продукция
            ('Б-М8х20', 'Болт М8х20 оцинкованный', 'Метизная продукция', 'Болты'),
            ('В-М6х15', 'Винт М6х15 нержавеющий', 'Метизная продукция', 'Винты'),
            ('Г-М8', 'Гайка М8 оцинкованная', 'Метизная продукция', 'Гайки'),
            ('З-4х10', 'Заклепка 4х10 алюминиевая', 'Метизная продукция', 'Заклепки'),
            ('О-20х200', 'Ось 20х200 стальная', 'Метизная продукция', 'Оси'),
            ('ШП-8', 'Шайба пружинная 8мм', 'Метизная продукция', 'Шайбы пружинные'),
            ('Ш-М10х80', 'Шпилька М10х80 резьбовая', 'Метизная продукция', 'Шпилька'),
            
            # Прочие категории без подкатегорий
            ('ПТ-001', 'Прочая техника универсальная', 'Прочая техника', None),
            ('БП-500', 'Бункер-перегрузчик 500л', 'Бункеры-перегрузчики', None),
            ('НОВ-001', 'Новинка 2025 года', 'Новинки', None),
            ('УСЛ-001', 'Техническое обслуживание', 'Прочие товары, работы и услуги', None),
            ('РС-001', 'Режущая система универсальная', 'Режущие системы жаток', None),
            ('СН-200', 'Самоходные носилки грузоподъемность 200кг', 'Самоходные носилки', None),
        ]
        
        for article, name, category_name, subcategory_name in sample_products:
            try:
                # Определяем категорию для товара
                if subcategory_name:
                    # Товар идет в подкатегорию
                    target_category = Category.objects.get(
                        name=subcategory_name, 
                        parent__name=category_name
                    )
                else:
                    # Товар идет прямо в основную категорию
                    target_category = Category.objects.get(
                        name=category_name, 
                        parent__isnull=True
                    )
                
                # Проверяем, существует ли товар
                if not Product.objects.filter(article=article).exists():
                    product = Product.objects.create(
                        name=name,
                        article=article,
                        slug=self.generate_unique_slug(f"{name}-{article}"),
                        description=f'Высококачественный товар {name} производства ОАО "ГЗЛиН"',
                        category=target_category,
                        price=Decimal(str(random.randint(50000, 3000000))),
                        stock_quantity=random.randint(1, 20),
                        is_active=True,
                        is_published=True,
                        is_featured=random.choice([True, False])
                    )
                    created_products += 1
                    self.stdout.write(f'    ✓ Создан товар: {name} ({article})')
                else:
                    self.stdout.write(f'      Товар уже существует: {article}')
                    
            except Category.DoesNotExist:
                self.stdout.write(f'❌ Категория не найдена для товара {article}: {category_name} -> {subcategory_name}')
            except Exception as e:
                self.stdout.write(f'❌ Ошибка создания товара {article}: {e}')
        
        # Статистика
        self.stdout.write(f'\n📊 Статистика загрузки:')
        self.stdout.write(f'  Основных категорий создано: {created_categories}')
        self.stdout.write(f'  Подкатегорий создано: {created_subcategories}')
        self.stdout.write(f'  Товаров создано: {created_products}')
        self.stdout.write(f'  Всего категорий в БД: {Category.objects.count()}')
        self.stdout.write(f'  Всего товаров в БД: {Product.objects.count()}')
        self.stdout.write('✅ Загрузка данных завершена!')
        
        # Выводим структуру для проверки
        self.stdout.write('\n🔍 Структура каталога:')
        main_categories = Category.objects.filter(parent__isnull=True).order_by('sort_order')
        for cat in main_categories:
            product_count = cat.get_products_count()
            self.stdout.write(f'  📁 {cat.name} ({product_count} товаров)')
            for subcat in cat.children.filter(is_active=True).order_by('sort_order'):
                sub_product_count = subcat.products.filter(is_active=True, is_published=True).count()
                self.stdout.write(f'    📂 {subcat.name} ({sub_product_count} товаров)')

    def generate_unique_slug(self, text):
        """Генерирует уникальный slug"""
        base_slug = slugify(text)
        slug = base_slug
        counter = 1
        
        while Category.objects.filter(slug=slug).exists() or Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug