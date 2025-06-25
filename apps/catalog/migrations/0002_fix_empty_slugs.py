# apps/catalog/migrations/0002_fix_empty_slugs.py
from django.db import migrations
from django.utils.text import slugify

def fix_empty_slugs(apps, schema_editor):
    """Исправляем пустые slug'и у категорий"""
    Category = apps.get_model('catalog', 'Category')
    
    # Находим категории с пустыми slug'ами
    categories_with_empty_slugs = Category.objects.filter(slug='')
    
    for category in categories_with_empty_slugs:
        if category.name:
            # Создаем slug из названия
            base_slug = slugify(category.name)
            
            # Проверяем уникальность
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            category.slug = slug
            category.save()
        else:
            # Если у категории нет названия, создаем временный slug
            category.slug = f"category-{category.id}"
            category.save()

def reverse_fix_empty_slugs(apps, schema_editor):
    """Обратная операция (если нужно откатить)"""
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('catalog', '0001_initial'),  # Замените на актуальную последнюю миграцию
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs, reverse_fix_empty_slugs),
    ]