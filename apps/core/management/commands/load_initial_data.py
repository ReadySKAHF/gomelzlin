from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Загружает категории и примеры товаров'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка категорий и товаров...')
        
        # Структура категорий
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
        
        # Создаем категории
        for category_name, subcategories in categories_data.items():
            # Создаем основную категорию
            main_category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={
                    'slug': slugify(category_name),
                    'description': f'Категория {category_name}',
                    'is_featured': True,
                    'sort_order': list(categories_data.keys()).index(category_name) + 1
                }
            )
            
            if created:
                self.stdout.write(f'  ✓ Создана категория: {category_name}')
            
            # Создаем подкатегории
            for i, subcategory_name in enumerate(subcategories):
                subcategory, created = Category.objects.get_or_create(
                    name=subcategory_name,
                    parent=main_category,
                    defaults={
                        'slug': slugify(subcategory_name),
                        'description': f'Подкатегория {subcategory_name}',
                        'sort_order': i + 1
                    }
                )
                
                if created:
                    self.stdout.write(f'    ✓ Создана подкатегория: {subcategory_name}')
        
        # Создаем примеры товаров
        self.create_sample_products()
        
        self.stdout.write(
            self.style.SUCCESS('Категории и товары успешно загружены!')
        )

    def create_sample_products(self):
        """Создает примеры товаров для каждой категории"""
        
        # Примеры товаров по категориям
        products_data = {
            # Зерноуборочная техника
            'Жатки валковые навесные': [
                ('Жатка валковая навесная ЖВН-6', 'ЖВН-6-001', 'Навесная жатка для скашивания зерновых культур в валки'),
                ('Жатка валковая ЖВН-4', 'ЖВН-4-001', 'Компактная навесная жатка шириной захвата 4 метра'),
            ],
            'Жатки валковые прицепные': [
                ('Жатка валковая прицепная ЖВП-8', 'ЖВП-8-001', 'Прицепная жатка большой производительности'),
                ('Жатка ЖВП-6', 'ЖВП-6-001', 'Универсальная прицепная жатка для различных культур'),
            ],
            'Жатки для зерновых культур': [
                ('Жатка зерновая ЖЗ-7', 'ЖЗ-7-001', 'Специализированная жатка для уборки зерновых'),
                ('Жатка ЖЗ-5М', 'ЖЗ-5М-001', 'Модернизированная жатка с улучшенными характеристиками'),
            ],
            'Жатки для уборки подсолнечника': [
                ('Жатка подсолнечниковая ЖПС-6', 'ЖПС-6-001', 'Специализированная жатка для уборки подсолнечника'),
                ('Жатка ЖПС-4', 'ЖПС-4-001', 'Компактная жатка для малых хозяйств'),
            ],
            
            # Кормоуборочная техника  
            'Жатки для грубостебельных культур': [
                ('Жатка ЖГС-4', 'ЖГС-4-001', 'Жатка для уборки кукурузы и других грубостебельных культур'),
            ],
            'Косилки': [
                ('Косилка роторная КР-2.8', 'КР-2.8-001', 'Роторная косилка для скашивания трав'),
                ('Косилка КДН-210', 'КДН-210-001', 'Дисковая навесная косилка'),
            ],
            
            # Метизная продукция
            'Болты': [
                ('Болт М8х25', 'БМ8-25', 'Болт с шестигранной головкой М8х25 мм'),
                ('Болт М10х30', 'БМ10-30', 'Болт с шестигранной головкой М10х30 мм'),
                ('Болт М12х40', 'БМ12-40', 'Болт с шестигранной головкой М12х40 мм'),
            ],
            'Гайки': [
                ('Гайка М8', 'ГМ8', 'Гайка шестигранная М8'),
                ('Гайка М10', 'ГМ10', 'Гайка шестигранная М10'),
                ('Гайка М12', 'ГМ12', 'Гайка шестигранная М12'),
            ],
            'Шайбы пружинные': [
                ('Шайба пружинная М8', 'ШП8', 'Шайба пружинная (гровер) М8'),
                ('Шайба пружинная М10', 'ШП10', 'Шайба пружинная (гровер) М10'),
            ],
            
            # Прочие категории
            'Картофелеуборочная техника': [
                ('Картофелеуборочный комбайн КУК-2', 'КУК-2-001', 'Двухрядный картофелеуборочный комбайн'),
                ('Картофелекопатель КТН-2В', 'КТН-2В-001', 'Навесной картофелекопатель'),
            ],
            'Бункеры-перегрузчики': [
                ('Бункер-перегрузчик БП-8', 'БП-8-001', 'Прицепной бункер-перегрузчик зерна'),
                ('Бункер БП-6М', 'БП-6М-001', 'Модернизированный бункер-перегрузчик'),
            ],
        }
        
        for category_name, products in products_data.items():
            try:
                # Находим категорию (может быть подкатегорией)
                category = Category.objects.filter(name=category_name).first()
                if not category:
                    continue
                
                for product_name, article, description in products:
                    # Проверяем, не существует ли уже товар с таким артикулом
                    if not Product.objects.filter(article=article).exists():
                        # Генерируем случайную цену
                        if 'М8' in article or 'М10' in article:
                            price = Decimal(str(round(random.uniform(0.5, 2.5), 2)))
                        elif any(x in category_name.lower() for x in ['болт', 'гайка', 'шайба']):
                            price = Decimal(str(round(random.uniform(1.0, 15.0), 2)))
                        else:
                            price = Decimal(str(round(random.uniform(15000, 180000), 2)))
                        
                        product = Product.objects.create(
                            name=product_name,
                            slug=slugify(f'{product_name}-{article}'),
                            article=article,
                            category=category,
                            description=description,
                            short_description=description[:200],
                            price=price,
                            stock_quantity=random.randint(5, 100),
                            unit='pcs',
                            status='published',
                            is_published=True,
                            is_featured=random.choice([True, False]),
                            weight=Decimal(str(round(random.uniform(0.1, 1500.0), 2))),
                        )
                        
                        self.stdout.write(f'    ✓ Создан товар: {product_name} ({article})')
                        
            except Exception as e:
                self.stdout.write(f'    ❌ Ошибка при создании товаров для {category_name}: {e}')