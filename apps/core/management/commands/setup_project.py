# apps/core/management/commands/setup_project.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Полная настройка проекта ОАО "ГЗЛиН"'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@gomelzlin.by',
            help='Email администратора'
        )
        parser.add_argument(
            '--admin-password',
            type=str,
            default='admin123456',
            help='Пароль администратора'
        )
        parser.add_argument(
            '--skip-data',
            action='store_true',
            help='Пропустить загрузку данных'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Начинаем настройку проекта ОАО "ГЗЛиН"...')
        )
        
        # 1. Создание суперпользователя
        self.create_superuser(options['admin_email'], options['admin_password'])
        
        # 2. Создание необходимых директорий
        self.create_directories()
        
        # 3. Загрузка данных
        if not options['skip_data']:
            self.load_initial_data()
        
        # 4. Создание базовых страниц
        self.create_basic_pages()
        
        # 5. Финальная статистика
        self.show_final_stats()
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Настройка проекта завершена успешно!')
        )
        self.stdout.write(
            self.style.WARNING('\n📝 Данные для входа в админку:')
        )
        self.stdout.write(f'   Email: {options["admin_email"]}')
        self.stdout.write(f'   Пароль: {options["admin_password"]}')
        self.stdout.write(f'   URL: http://localhost:8000/admin/')

    def create_superuser(self, email, password):
        """Создание суперпользователя"""
        User = get_user_model()
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠ Пользователь с email {email} уже существует')
            )
            return
        
        try:
            user = User.objects.create_superuser(
                email=email,
                password=password,
                first_name='Администратор',
                last_name='ГЗЛиН'
            )
            self.stdout.write(
                self.style.SUCCESS(f'✓ Создан суперпользователь: {email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка создания суперпользователя: {e}')
            )

    def create_directories(self):
        """Создание необходимых директорий"""
        directories = [
            'media/categories',
            'media/products',
            'media/companies',
            'media/users',
            'static/admin',
            'staticfiles',
        ]
        
        for directory in directories:
            full_path = os.path.join(settings.BASE_DIR, directory)
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
                self.stdout.write(f'✓ Создана директория: {directory}')

    def load_initial_data(self):
        """Загрузка начальных данных"""
        from django.core.management import call_command
        
        self.stdout.write('\n📦 Загружаем данные...')
        
        try:
            # Загружаем категории и товары
            call_command('load_initial_data')
            self.stdout.write(
                self.style.SUCCESS('✓ Категории и товары загружены')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Ошибка загрузки данных: {e}')
            )

    def create_basic_pages(self):
        """Создание базовых страниц"""
        self.stdout.write('\n📄 Создаем базовые страницы...')
        
        # Здесь можно добавить создание базовых страниц
        # Например, информация о компании, контакты и т.д.
        
        self.create_company_info()
        self.create_management_team()
        self.create_partners()

    def create_company_info(self):
        """Создание информации о компании"""
        try:
            from apps.company.models import CompanyInfo
            
            if not CompanyInfo.objects.exists():
                CompanyInfo.objects.create(
                    full_name='Открытое акционерное общество "Гомельский завод литейных изделий и нормалей"',
                    short_name='ОАО "ГЗЛиН"',
                    brand_name='ГЗЛиН',
                    founded_year=1965,
                    description='''ОАО "ГЗЛиН" - ведущий производитель литейных изделий и сельскохозяйственной техники 
                    в Республике Беларусь. Предприятие специализируется на производстве жатвенных агрегатов, 
                    кормоуборочной техники, метизных изделий и другого промышленного оборудования.''',
                    mission='''Обеспечение аграрного сектора Беларуси и стран СНГ качественной и надежной 
                    сельскохозяйственной техникой и промышленными изделиями.''',
                    phone='+375 232 12-34-56',
                    email='info@gomelzlin.by',
                    legal_address='246000, г. Гомель, ул. Промышленная, 15',
                    postal_address='246000, г. Гомель, ул. Промышленная, 15'
                )
                self.stdout.write('✓ Создана информация о компании')
        except Exception as e:
            self.stdout.write(f'⚠ Ошибка создания информации о компании: {e}')

    def create_management_team(self):
        """Создание команды руководства"""
        try:
            from apps.company.models import ManagementMember
            
            if not ManagementMember.objects.exists():
                management_data = [
                    {
                        'full_name': 'Иванов Иван Иванович',
                        'position': 'Генеральный директор',
                        'email': 'director@gomelzlin.by',
                        'phone': '+375 232 12-34-57',
                        'bio': 'Опыт работы в машиностроении более 20 лет.',
                        'sort_order': 1
                    },
                    {
                        'full_name': 'Петров Петр Петрович',
                        'position': 'Технический директор',
                        'email': 'tech@gomelzlin.by',
                        'phone': '+375 232 12-34-58',
                        'bio': 'Специалист по разработке сельскохозяйственной техники.',
                        'sort_order': 2
                    },
                    {
                        'full_name': 'Сидорова Анна Сергеевна',
                        'position': 'Коммерческий директор',
                        'email': 'sales@gomelzlin.by',
                        'phone': '+375 232 12-34-59',
                        'bio': 'Отвечает за развитие продаж и работу с клиентами.',
                        'sort_order': 3
                    }
                ]
                
                for member_data in management_data:
                    ManagementMember.objects.create(**member_data)
                
                self.stdout.write('✓ Создана команда руководства')
        except Exception as e:
            self.stdout.write(f'⚠ Ошибка создания команды руководства: {e}')

    def create_partners(self):
        """Создание списка партнеров"""
        try:
            from apps.company.models import Partner
            
            if not Partner.objects.exists():
                partners_data = [
                    {
                        'name': 'ОАО "БЕЛАЗ"',
                        'description': 'Ведущий производитель карьерной техники. Многолетнее сотрудничество в области поставок литейных изделий.',
                        'website': 'https://belaz.by',
                        'sort_order': 1
                    },
                    {
                        'name': 'ОАО "МТЗ"',
                        'description': 'Минский тракторный завод. Поставка специализированных литейных изделий для тракторной промышленности.',
                        'website': 'https://mtz.by',
                        'sort_order': 2
                    },
                    {
                        'name': 'ОАО "МАЗ"',
                        'description': 'Минский автомобильный завод. Партнерство в производстве компонентов для грузовых автомобилей.',
                        'website': 'https://maz.by',
                        'sort_order': 3
                    }
                ]
                
                for partner_data in partners_data:
                    Partner.objects.create(**partner_data)
                
                self.stdout.write('✓ Создан список партнеров')
        except Exception as e:
            self.stdout.write(f'⚠ Ошибка создания партнеров: {e}')

    def show_final_stats(self):
        """Показ финальной статистики"""
        try:
            from apps.catalog.models import Category, Product
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            
            stats = {
                'Пользователи': User.objects.count(),
                'Категории': Category.objects.count(),
                'Товары': Product.objects.count(),
                'Опубликованные товары': Product.objects.filter(is_published=True).count(),
                'Рекомендуемые товары': Product.objects.filter(is_featured=True).count(),
            }
            
            self.stdout.write('\n📊 Статистика проекта:')
            for key, value in stats.items():
                self.stdout.write(f'   {key}: {value}')
                
        except Exception as e:
            self.stdout.write(f'⚠ Ошибка получения статистики: {e}')