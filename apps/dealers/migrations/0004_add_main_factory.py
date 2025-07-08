from django.db import migrations


def add_main_factory(apps, schema_editor):
    """Добавляем главный завод ОАО ГЗЛиН"""
    DealerCenter = apps.get_model('dealers', 'DealerCenter')

    if not DealerCenter.objects.filter(dealer_type='factory').exists():
        DealerCenter.objects.create(
            name='ОАО "ГЗЛиН"',
            full_name='Открытое акционерное общество "Гомельский завод литейных изделий и нормалей"',
            dealer_type='factory',
            contact_person='Руководство завода',
            position='Администрация',
            phone='+375232123456',
            email='info@gomelzlin.by',
            website='https://gomelzlin.by',
            region='gomel',
            city='Гомель',
            address='ул. Могилёвская, 16',
            postal_code='246010',
            latitude=52.4345,
            longitude=30.9754,
            working_hours='Пн-Пт: 8:00-17:00\nСб: выходной\nВс: выходной',
            description='Главный завод литейных изделий и нормалей. Основан в 1965 году. Ведущий производитель литейной продукции в Республике Беларусь.',
            is_featured=True,
            is_verified=True,
            is_active=True,
            sort_order=1,
        )


def remove_main_factory(apps, schema_editor):
    """Удаляем главный завод"""
    DealerCenter = apps.get_model('dealers', 'DealerCenter')
    DealerCenter.objects.filter(
        name='ОАО "ГЗЛиН"',
        dealer_type='factory'
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0003_add_factory_type'),
    ]

    operations = [
        migrations.RunPython(add_main_factory, remove_main_factory),
    ]