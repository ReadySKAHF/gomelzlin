from django.core.management.base import BaseCommand
from apps.catalog.models import Category


class Command(BaseCommand):
    help = 'Автоматически исправляет slug для всех категорий ОАО ГЗЛиН'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Исправление slug\'ов для всех категорий ОАО "ГЗЛиН"...')
        self.stdout.write('=' * 60)
        
        # Предопределенные правильные slug'ы
        CATEGORY_SLUGS = {
            'Зерноуборочная техника': 'zernoubobochnaya-tehnika',
            'Кормоуборочная техника': 'kormoubobochnaya-tehnika',
            'Картофелеуборочная техника': 'kartofeleubobochnaya-tehnika',
            'Метизная продукция': 'metiznaya-produkcziya',
            'Прочая техника': 'prochaya-tehnika',
            'Бункеры-перегрузчики': 'bunkery-peregruzchiki',
            'Новинки': 'novinki',
            'Прочие товары, работы и услуги': 'prochie-tovary-raboty-uslugi',
            'Режущие системы жаток': 'rezhushhie-sistemy-zhatok',
            'Самоходные носилки': 'samohodnye-nosilki',
        }
        
        fixed_count = 0
        not_found_count = 0
        
        for category_name, correct_slug in CATEGORY_SLUGS.items():
            try:
                category = Category.objects.get(name=category_name)
                old_slug = category.slug
                
                if category.slug != correct_slug:
                    category.slug = correct_slug
                    category.save()
                    
                    self.stdout.write(f'✅ {category_name}')
                    self.stdout.write(f'   Старый slug: "{old_slug}" -> Новый: "{correct_slug}"')
                    self.stdout.write(f'   URL: /catalog/category/{correct_slug}/')
                    fixed_count += 1
                else:
                    self.stdout.write(f'✓  {category_name} (уже правильный: "{correct_slug}")')
                
                self.stdout.write('-' * 50)
                
            except Category.DoesNotExist:
                self.stdout.write(f'❌ Категория "{category_name}" не найдена в БД')
                not_found_count += 1
                self.stdout.write('-' * 50)
        
        # Финальная проверка всех категорий
        self.stdout.write('\n📋 Финальная проверка всех категорий в БД:')
        self.stdout.write('=' * 60)
        
        all_categories = Category.objects.all().order_by('id')
        for category in all_categories:
            try:
                url = category.get_absolute_url()
                status = "✅" if category.slug and category.slug.strip() else "❌"
                self.stdout.write(f'{status} ID {category.id}: {category.name}')
                self.stdout.write(f'    Slug: "{category.slug}"')
                self.stdout.write(f'    URL:  {url}')
                self.stdout.write('')
            except Exception as e:
                self.stdout.write(f'❌ ID {category.id}: {category.name} - Ошибка: {e}')
                self.stdout.write('')
        
        # Итоговая статистика
        self.stdout.write('📊 Статистика:')
        self.stdout.write('=' * 60)
        self.stdout.write(f'🔧 Исправлено категорий: {fixed_count}')
        self.stdout.write(f'❌ Не найдено категорий: {not_found_count}')
        self.stdout.write(f'📝 Всего категорий в БД: {all_categories.count()}')
        
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 Успешно исправлено {fixed_count} категорий!'))
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Все slug\'ы уже корректные!'))
        
        self.stdout.write(self.style.SUCCESS('\n🚀 Теперь откройте http://127.0.0.1:8000/catalog/ и проверьте результат!'))