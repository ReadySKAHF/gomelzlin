from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.core.models import SiteSettings
from apps.company.models import CompanyInfo, Leader
from apps.catalog.models import Category
from apps.dealers.models import DealerCenter

User = get_user_model()


class Command(BaseCommand):
    help = 'Загружает начальные данные для сайта'

    def handle(self, *args, **options):
        self.stdout.write('Загрузка начальных данных...')
        
        # Создаем настройки сайта
        self.create_site_settings()
        
        # Создаем информацию о компании
        self.create_company_info()
        
        # Создаем руководство
        self.create_leadership()
        
        # Создаем категории
        self.create_categories()
        
        # Создаем дилерские центры
        self.create_dealers()
        
        self.stdout.write(
            self.style.SUCCESS('Начальные данные успешно загружены!')
        )

    def create_site_settings(self):
        """Создает настройки сайта"""
        settings, created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                'company_name': 'ОАО "Гомельский завод литейных изделий и нормалей"',
                'company_short_name': 'ГЗЛиН',
                'phone': '+375 232 12-34-56',
                'email': 'info@gomelzlin.by',
                'address': '246000, г. Гомель, ул. Промышленная, 15',
                'working_hours': 'Пн-Пт: 8:00-17:00\nСб-Вс: выходной',
                'min_order_amount': 100.00,
                'order_notification_email': 'orders@gomelzlin.by',
                'admin_notification_email': 'admin@gomelzlin.by',
            }
        )
        if created:
            self.stdout.write('  ✓ Настройки сайта созданы')

    def create_company_info(self):
        """Создает информацию о компании"""
        info, created = CompanyInfo.objects.get_or_create(
            pk=1,
            defaults={
                'full_name': 'Открытое акционерное общество "Гомельский завод литейных изделий и нормалей"',
                'short_name': 'ОАО "ГЗЛиН"',
                'brand_name': 'ГЗЛиН',
                'founded_year': 1965,
                'mission': 'Обеспечение промышленности Беларуси и стран СНГ высококачественными литейными изделиями и нормалями.',
                'description': 'Ведущий производитель литейных изделий и нормалей в Республике Беларусь с 1965 года.',
                'phone': '+375 232 12-34-56',
                'email': 'info@gomelzlin.by',
                'legal_address': '246000, г. Гомель, ул. Промышленная, 15',
                'unp': '400123456',
            }
        )
        if created:
            self.stdout.write('  ✓ Информация о компании создана')

    def create_leadership(self):
        """Создает руководство"""
        leaders_data = [
            {
                'first_name': 'Иван',
                'last_name': 'Иванов',
                'middle_name': 'Иванович',
                'position': 'Генеральный директор',
                'position_type': 'director',
                'email': 'director@gomelzlin.by',
                'phone': '+375 232 12-34-56',
                'sort_order': 1,
            },
            {
                'first_name': 'Анна',
                'last_name': 'Петрова',
                'middle_name': 'Сергеевна',
                'position': 'Технический директор',
                'position_type': 'deputy_director',
                'email': 'tech@gomelzlin.by',
                'phone': '+375 232 12-34-57',
                'sort_order': 2,
            },
            {
                'first_name': 'Петр',
                'last_name': 'Сидоров',
                'middle_name': 'Алексеевич',
                'position': 'Коммерческий директор',
                'position_type': 'deputy_director',
                'email': 'sales@gomelzlin.by',
                'phone': '+375 232 12-34-58',
                'sort_order': 3,
            },
        ]
        
        for leader_data in leaders_data:
            leader, created = Leader.objects.get_or_create(
                email=leader_data['email'],
                defaults=leader_data
            )
            if created:
                self.stdout.write(f'  ✓ Руководитель {leader.get_full_name()} создан')

    def create_categories(self):
        """Создает категории товаров"""
        # Создаем основные категории
        fittings, created = Category.objects.get_or_create(
            slug='fittings',
            defaults={
                'name': 'Фитинги',
                'description': 'Широкий ассортимент фитингов для трубопроводов различного назначения',
                'icon': '🔧',
                'is_featured': True,
                'sort_order': 1,
            }
        )
        
        valves, created = Category.objects.get_or_create(
            slug='valves',
            defaults={
                'name': 'Трубопроводная арматура',
                'description': 'Краны, вентили, задвижки и другая запорная арматура',
                'icon': '🚰',
                'is_featured': True,
                'sort_order': 2,
            }
        )
        
        castings, created = Category.objects.get_or_create(
            slug='castings',
            defaults={
                'name': 'Литейные изделия',
                'description': 'Отливки из различных сплавов по индивидуальным заказам',
                'icon': '🏭',
                'is_featured': True,
                'sort_order': 3,
            }
        )
        
        # Создаем подкategории для фитингов
        subcategories = [
            {'name': 'Уголки', 'parent': fittings, 'slug': 'angles'},
            {'name': 'Тройники', 'parent': fittings, 'slug': 'tees'},
            {'name': 'Переходники', 'parent': fittings, 'slug': 'adapters'},
        ]
        
        for subcat_data in subcategories:
            subcat, created = Category.objects.get_or_create(
                slug=subcat_data['slug'],
                defaults=subcat_data
            )
            if created:
                self.stdout.write(f'  ✓ Категория {subcat.name} создана')

    def create_dealers(self):
        """Создает дилерские центры"""
        dealers_data = [
            {
                'name': 'Дилерский центр Минск',
                'region': 'minsk_city',
                'city': 'Минск',
                'address': 'пр. Независимости, 125',
                'contact_person': 'Сергей Минский',
                'phone': '+375171234567',
                'email': 'minsk@gomelzlin.by',
                'dealer_type': 'official',
                'is_featured': True,
            },
            {
                'name': 'Дилерский центр Брест',
                'region': 'brest',
                'city': 'Брест',
                'address': 'ул. Московская, 45',
                'contact_person': 'Анна Брестская',
                'phone': '+375162123456',
                'email': 'brest@gomelzlin.by',
                'dealer_type': 'authorized',
            },
            {
                'name': 'Дилерский центр Витебск',
                'region': 'vitebsk',
                'city': 'Витебск',
                'address': 'ул. Ленина, 78',
                'contact_person': 'Николай Витебский',
                'phone': '+375212123456',
                'email': 'vitebsk@gomelzlin.by',
                'dealer_type': 'authorized',
            },
        ]
        
        for dealer_data in dealers_data:
            dealer, created = DealerCenter.objects.get_or_create(
                email=dealer_data['email'],
                defaults=dealer_data
            )
            if created:
                self.stdout.write(f'  ✓ Дилер {dealer.name} создан')