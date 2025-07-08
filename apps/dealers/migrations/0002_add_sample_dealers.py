from django.db import migrations


def create_sample_dealers(apps, schema_editor):
    """Создание примеров дилерских центров"""
    DealerCenter = apps.get_model('dealers', 'DealerCenter')
    
    sample_dealers = [
        {
            'name': 'Дилерский центр Минск',
            'full_name': 'ООО "ГЗЛиН-Минск"',
            'dealer_type': 'official',
            'contact_person': 'Иванов Петр Сергеевич',
            'position': 'Главный региональный менеджер',
            'phone': '+375171234567',
            'email': 'minsk@gomelzlin.by',
            'website': 'https://minsk.gomelzlin.by',
            'region': 'minsk_city',
            'city': 'Минск',
            'address': 'пр. Независимости, 125',
            'postal_code': '220004',
            'latitude': 53.9045,
            'longitude': 27.5615,
            'working_hours': 'Пн-Пт: 8:00-17:00\nСб: 9:00-14:00\nВс: выходной',
            'description': 'Главный дилерский центр в столице. Полный ассортимент продукции, консультации специалистов.',
            'is_featured': True,
            'is_verified': True,
            'is_active': True,
            'sort_order': 1,
        },
        {
            'name': 'Дилерский центр Брест',
            'full_name': 'ИП Петров А.В.',
            'dealer_type': 'authorized',
            'contact_person': 'Петров Алексей Викторович',
            'position': 'Директор',
            'phone': '+375162234567',
            'email': 'brest@gomelzlin.by',
            'region': 'brest',
            'city': 'Брест',
            'address': 'ул. Московская, 45',
            'postal_code': '224016',
            'latitude': 52.0975,
            'longitude': 23.7342,
            'working_hours': 'Пн-Пт: 9:00-18:00\nСб: 9:00-15:00\nВс: выходной',
            'description': 'Авторизованный дилер в Бресте. Быстрая доставка по западному региону.',
            'is_featured': True,
            'is_verified': True,
            'is_active': True,
            'sort_order': 2,
        },
        {
            'name': 'Дилерский центр Витебск',
            'full_name': 'ООО "Северный металл"',
            'dealer_type': 'partner',
            'contact_person': 'Сидорова Елена Николаевна',
            'position': 'Коммерческий директор',
            'phone': '+375212345678',
            'email': 'vitebsk@gomelzlin.by',
            'region': 'vitebsk',
            'city': 'Витебск',
            'address': 'ул. Ленина, 78',
            'postal_code': '210026',
            'latitude': 55.1904,
            'longitude': 30.2049,
            'working_hours': 'Пн-Пт: 9:00-17:00\nСб: 10:00-14:00\nВс: выходной',
            'description': 'Партнерский центр в Витебске. Специализация на промышленном оборудовании.',
            'is_featured': False,
            'is_verified': True,
            'is_active': True,
            'sort_order': 3,
        },
        {
            'name': 'Дилерский центр Гродно',
            'full_name': 'ЧУП "Западстройсервис"',
            'dealer_type': 'distributor',
            'contact_person': 'Козлов Дмитрий Александрович',
            'position': 'Заместитель директора',
            'phone': '+375152456789',
            'email': 'grodno@gomelzlin.by',
            'region': 'grodno',
            'city': 'Гродно',
            'address': 'ул. Богдановича, 16',
            'postal_code': '230023',
            'latitude': 53.6884,
            'longitude': 23.8258,
            'working_hours': 'Пн-Пт: 8:30-17:30\nСб: 9:00-13:00\nВс: выходной',
            'description': 'Дистрибьютор в Гродно. Обслуживание крупных промышленных предприятий.',
            'is_featured': False,
            'is_verified': True,
            'is_active': True,
            'sort_order': 4,
        },
        {
            'name': 'Дилерский центр Могилев',
            'full_name': 'ООО "Восточный металлоторг"',
            'dealer_type': 'authorized',
            'contact_person': 'Морозов Сергей Иванович',
            'position': 'Региональный менеджер',
            'phone': '+375222567890',
            'email': 'mogilev@gomelzlin.by',
            'region': 'mogilev',
            'city': 'Могилев',
            'address': 'ул. Первомайская, 89',
            'postal_code': '212030',
            'latitude': 53.9168,
            'longitude': 30.3449,
            'working_hours': 'Пн-Пт: 9:00-18:00\nСб: 9:00-15:00\nВс: выходной',
            'description': 'Авторизованный дилер в Могилеве. Широкий выбор арматуры и фитингов.',
            'is_featured': False,
            'is_verified': True,
            'is_active': True,
            'sort_order': 5,
        },
        {
            'name': 'Дилерский центр Гомель',
            'full_name': 'ООО "ГЗЛиН-Юг"',
            'dealer_type': 'official',
            'contact_person': 'Никитин Владимир Петрович',
            'position': 'Директор филиала',
            'phone': '+375232678901',
            'email': 'gomel@gomelzlin.by',
            'website': 'https://gomel.gomelzlin.by',
            'region': 'gomel',
            'city': 'Гомель',
            'address': 'пр. Октября, 15',
            'postal_code': '246050',
            'latitude': 52.4411,
            'longitude': 30.9878,
            'working_hours': 'Пн-Пт: 8:00-17:00\nСб: 9:00-14:00\nВс: выходной',
            'description': 'Официальный дилер в Гомеле. Близость к основному производству обеспечивает минимальные сроки поставки.',
            'is_featured': True,
            'is_verified': True,
            'is_active': True,
            'sort_order': 6,
        },
    ]
    
    for dealer_data in sample_dealers:
        DealerCenter.objects.get_or_create(
            name=dealer_data['name'],
            city=dealer_data['city'],
            defaults=dealer_data
        )


def remove_sample_dealers(apps, schema_editor):
    """Удаление примеров дилерских центров"""
    DealerCenter = apps.get_model('dealers', 'DealerCenter')
    
    sample_names = [
        'Дилерский центр Минск',
        'Дилерский центр Брест',
        'Дилерский центр Витебск',
        'Дилерский центр Гродно',
        'Дилерский центр Могилев',
        'Дилерский центр Гомель',
    ]
    
    DealerCenter.objects.filter(name__in=sample_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_sample_dealers, remove_sample_dealers),
    ]