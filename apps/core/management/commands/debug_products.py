# apps/core/management/commands/debug_products.py
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Проверяет товары и их URL для диагностики проблем'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Диагностика товаров и их URL...'))
        
        # 1. Проверяем общую статистику
        categories_count = Category.objects.count()
        products_count = Product.objects.count()
        active_products = Product.objects.filter(is_active=True, is_published=True).count()
        
        self.stdout.write(f'\n📊 Статистика:')
        self.stdout.write(f'   Всего категорий: {categories_count}')
        self.stdout.write(f'   Всего товаров: {products_count}')
        self.stdout.write(f'   Активных товаров: {active_products}')
        
        # 2. Проверяем первые несколько товаров
        self.stdout.write(f'\n🔍 Проверяем первые 5 товаров:')
        self.stdout.write('=' * 80)
        
        products = Product.objects.filter(is_active=True, is_published=True)[:5]
        
        for i, product in enumerate(products, 1):
            self.stdout.write(f'\n{i}. Товар: {product.name}')
            self.stdout.write(f'   ID: {product.id}')
            self.stdout.write(f'   Артикул: {product.article}')
            self.stdout.write(f'   Slug: "{product.slug}"')
            self.stdout.write(f'   Категория: {product.category.name}')
            self.stdout.write(f'   Slug категории: "{product.category.slug}"')
            
            # Проверяем URL
            try:
                url = product.get_absolute_url()
                self.stdout.write(f'   ✅ URL: {url}')
                
                # Проверяем, что это правильный URL
                if url.startswith('/catalog/product/') and product.slug in url:
                    self.stdout.write(f'   ✅ URL корректный')
                else:
                    self.stdout.write(f'   ❌ URL некорректный! Ожидался: /catalog/product/{product.slug}/')
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Ошибка URL: {e}')
            
            self.stdout.write('-' * 60)
        
        # 3. Проверяем конкретный товар из ошибки
        self.stdout.write(f'\n🎯 Ищем товар "zhatka-valkovaya-pricepnaya-4-metrovaya":')
        self.stdout.write('=' * 80)
        
        try:
            product = Product.objects.get(slug='zhatka-valkovaya-pricepnaya-4-metrovaya')
            self.stdout.write(f'✅ Товар найден!')
            self.stdout.write(f'   Название: {product.name}')
            self.stdout.write(f'   Slug: {product.slug}')
            self.stdout.write(f'   Категория: {product.category.name}')
            self.stdout.write(f'   URL: {product.get_absolute_url()}')
            self.stdout.write(f'   Активен: {product.is_active}')
            self.stdout.write(f'   Опубликован: {product.is_published}')
            
            # Проверяем URL напрямую
            correct_url = f'/catalog/product/{product.slug}/'
            actual_url = product.get_absolute_url()
            
            if actual_url == correct_url:
                self.stdout.write(f'   ✅ URL генерируется правильно')
                self.stdout.write(f'   👉 Попробуйте: http://127.0.0.1:8000{correct_url}')
            else:
                self.stdout.write(f'   ❌ URL неправильный!')
                self.stdout.write(f'   Ожидался: {correct_url}')
                self.stdout.write(f'   Получен: {actual_url}')
                
        except Product.DoesNotExist:
            self.stdout.write(f'❌ Товар с slug "zhatka-valkovaya-pricepnaya-4-metrovaya" НЕ найден!')
            
            # Ищем похожие товары
            similar_products = Product.objects.filter(
                slug__icontains='zhatka'
            )[:3]
            
            if similar_products.exists():
                self.stdout.write(f'\n🔍 Найдены похожие товары:')
                for prod in similar_products:
                    self.stdout.write(f'   - {prod.name} (slug: {prod.slug})')
            else:
                self.stdout.write(f'   Похожих товаров не найдено')
        
        # 4. Проверяем категорию из ошибки
        self.stdout.write(f'\n📁 Проверяем категорию "zhatki-valkovye-pricepnye":')
        self.stdout.write('=' * 80)
        
        try:
            category = Category.objects.get(slug='zhatki-valkovye-pricepnye')
            self.stdout.write(f'✅ Категория найдена!')
            self.stdout.write(f'   Название: {category.name}')
            self.stdout.write(f'   Slug: {category.slug}')
            self.stdout.write(f'   URL: {category.get_absolute_url()}')
            
            # Проверяем товары в этой категории
            products_in_category = category.products.filter(is_active=True, is_published=True)
            self.stdout.write(f'   Товаров в категории: {products_in_category.count()}')
            
            for prod in products_in_category[:3]:
                self.stdout.write(f'     - {prod.name} (slug: {prod.slug})')
                self.stdout.write(f'       URL: {prod.get_absolute_url()}')
                
        except Category.DoesNotExist:
            self.stdout.write(f'❌ Категория с slug "zhatki-valkovye-pricepnye" НЕ найдена!')
        
        # 5. Рекомендации
        self.stdout.write(f'\n💡 Рекомендации:')
        self.stdout.write('=' * 80)
        self.stdout.write('1. Проверьте товары в админке: http://127.0.0.1:8000/django-admin/catalog/product/')
        self.stdout.write('2. Убедитесь, что товары имеют slug и активны')
        self.stdout.write('3. Правильный URL товара: /catalog/product/SLUG/')
        self.stdout.write('4. НЕ используйте URL вида: /catalog/category/CAT_SLUG/PRODUCT_SLUG/')
        
        if products_count == 0:
            self.stdout.write(f'\n⚠️  ВНИМАНИЕ: В базе нет товаров!')
            self.stdout.write('   Запустите: python manage.py load_initial_data')
            self.stdout.write('   Или:       python manage.py fix_products')