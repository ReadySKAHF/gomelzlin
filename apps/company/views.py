from django.shortcuts import render
from django.views.generic import TemplateView

from django.shortcuts import render
from django.views.generic import TemplateView

from django.shortcuts import render
from django.views.generic import TemplateView

class AboutView(TemplateView):
    template_name = 'company/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О компании'
        # Добавляем данные партнёров
        context['partners'] = [
            {
                'name': 'ОАО "БЕЛАЗ"',
                'description': 'Ведущий производитель карьерной техники в мире',
                'website': 'https://belaz.by',
                'logo': 'images/partners/belaz.jpg'
            },
            {
                'name': 'ОАО "МТЗ"',
                'description': 'Минский тракторный завод - производитель сельхозтехники',
                'website': 'https://mtz.by',
                'logo': 'images/partners/mtz.jpg'
            },
            {
                'name': 'ОАО "МАЗ"',
                'description': 'Минский автомобильный завод',
                'website': 'https://maz.by',
                'logo': 'images/partners/maz.jpg'
            }
        ]
        # Добавляем данные руководства для использования в шаблоне about.html
        context['leaders'] = [
            {
                'name': 'Панфиленко Николай Николаевич',
                'position': 'Директор общества',
                'email': 'npanfilenko@gomelzlin.by',
                'phone': '+375-232-59-61-31',
                'photo': 'images/employees/panfilenko-nikolaj-nikolaevich.jpg'
            },
            {
                'name': 'Черношей Сергей Григорьевич',
                'position': 'Директор литейного производства',
                'email': 'gchernoshei@gomelzlin.by',
                'phone': '+375-232-14-63-47',
                'photo': 'images/employees/chernoshej-sergej-grigorevich.jpg'
            },
            {
                'name': 'Даниленко Евгений Леонидович',
                'position': 'Заместитель директора по техническим вопросам',
                'email': 'danilenko-el@gomelzlin.by',
                'phone': '+375-232-59-67-00',
                'photo': 'images/employees/danilenko-evgenij-leonidovich.jpg'
            },
            {
                'name': 'Бойцов Леонид Леонидович',
                'position': 'Заместитель директора по производству',
                'email': 'llboycov@gomelzlin.by',
                'phone': '+375-232-59-68-48',
                'photo': 'images/employees/bojcov-leonid-leonidovich.jpg'
            },
            {
                'name': 'Лозовой Андрей Николаевич',
                'position': 'Заместитель директора по коммерческим вопросам',
                'email': 'anlozovoy@gomelzlin.by',
                'phone': '+375-232-85-72-01',
                'photo': 'images/employees/lozovoj-andrej-nikolaevich.jpg'
            },
            {
                'name': 'Тимошенко Андрей Михайлович',
                'position': 'Заместитель директора по качеству',
                'email': 'otk@gomelzlin.by',
                'phone': '+375-232-59-60-83',
                'photo': 'images/employees/timoshenko-andrej-mihajlovich.jpg'
            },
            {
                'name': 'Станкевич Анатолий Иванович',
                'position': 'Заместитель директора по идеологической работе и управлению персоналом',
                'email': 'oir@gomelzlin.by',
                'phone': '+375-232-59-61-79',
                'photo': 'images/employees/stankevich-anatolij-ivanovich.jpg'
            },
            {
                'name': 'Павлюкова Виктория Петровна',
                'position': 'Начальник ОМТС',
                'email': 'omts@gomelzlin.by',
                'phone': '+375-232-59-62-33',
                'photo': 'images/employees/pavlyukova-viktoriya-petrovna.jpg'
            },
            {
                'name': 'Какора Надежда Адамовна',
                'position': 'Главный экономист',
                'email': 'kakora@gomelzlin.by',
                'phone': '+375-232-59-68-77',
                'photo': 'images/employees/kakora-nadezhda-adamovna.jpg'
            },
            {
                'name': 'Камко Татьяна Михайловна',
                'position': 'Главный бухгалтер',
                'email': 'buh@gomelzlin.by',
                'phone': '+375-232-59-69-64',
                'photo': 'images/employees/kamko-tatsyana-mihajlovna.jpg'
            },
            {
                'name': 'Мосензовенко Александр Викторович',
                'position': 'Главный технолог',
                'email': 'ogt@gomelzlin.by',
                'phone': '+375-232-59-61-86',
                'photo': 'images/employees/mosenzovenko-aleksandr-viktorovich.jpg'
            },
            {
                'name': 'Гасымов Владислав Гисматович',
                'position': 'Начальник отдела кадров',
                'email': 'ok@gomelzlin.by',
                'phone': '+375-232-59-67-97',
                'photo': 'images/employees/gasymov-vladislav-gismatovich.jpg'
            },
            {
                'name': 'Трашков Андрей Владимирович',
                'position': 'Начальник отдела продаж',
                'email': 'op@gomelzlin.by',
                'phone': '+375-232-59-65-14',
                'photo': 'images/employees/trashkov-andrej-vladimirovich.jpg'
            },
            {
                'name': 'Швайба Екатерина Васильевна',
                'position': 'Начальник центра маркетинговых коммуникаций',
                'email': 'om@gomelzlin.by',
                'phone': '+375-232-59-62-40',
                'photo': 'images/employees/shvajba-ekaterina-vasilevna.jpg'
            },
            {
                'name': 'Герасименко Юрий Валерьевич',
                'position': 'Начальник транспортного управления',
                'email': 'tto@gomelzlin.by',
                'phone': '+375-232-59-60-80',
                'photo': 'images/employees/gerasimenko-yurij-valerevich.jpg'
            },
            {
                'name': 'Давыдова Тамара Николаевна',
                'position': 'Начальник юридического отдела',
                'email': 'tmdavidova@gomelzlin.by',
                'phone': '+375-232-59-69-16',
                'photo': 'images/employees/davydova-tamara-nikolaevna.jpg'
            }
        ]
        return context

class LeadershipView(TemplateView):
    template_name = 'company/leadership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Руководство'
        context['leaders'] = [
            {
                'name': 'Панфиленко Николай Николаевич',
                'position': 'Директор общества',
                'email': 'npanfilenko@gomelzlin.by',
                'phone': '+375-232-59-61-31',
                'photo': 'images/employees/panfilenko-nikolaj-nikolaevich.jpg'
            },
            {
                'name': 'Черношей Сергей Григорьевич',
                'position': 'Директор литейного производства',
                'email': 'gchernoshei@gomelzlin.by',
                'phone': '+375-232-14-63-47',
                'photo': 'images/employees/chernoshej-sergej-grigorevich.jpg'
            },
            {
                'name': 'Даниленко Евгений Леонидович',
                'position': 'Заместитель директора по техническим вопросам',
                'email': 'danilenko-el@gomelzlin.by',
                'phone': '+375-232-59-67-00',
                'photo': 'images/employees/danilenko-evgenij-leonidovich.jpg'
            },
            {
                'name': 'Бойцов Леонид Леонидович',
                'position': 'Заместитель директора по производству',
                'email': 'llboycov@gomelzlin.by',
                'phone': '+375-232-59-68-48',
                'photo': 'images/employees/bojcov-leonid-leonidovich.jpg'
            },
            {
                'name': 'Лозовой Андрей Николаевич',
                'position': 'Заместитель директора по коммерческим вопросам',
                'email': 'anlozovoy@gomelzlin.by',
                'phone': '+375-232-85-72-01',
                'photo': 'images/employees/lozovoj-andrej-nikolaevich.jpg'
            },
            {
                'name': 'Тимошенко Андрей Михайлович',
                'position': 'Заместитель директора по качеству',
                'email': 'otk@gomelzlin.by',
                'phone': '+375-232-59-60-83',
                'photo': 'images/employees/timoshenko-andrej-mihajlovich.jpg'
            },
            {
                'name': 'Станкевич Анатолий Иванович',
                'position': 'Заместитель директора по идеологической работе и управлению персоналом',
                'email': 'oir@gomelzlin.by',
                'phone': '+375-232-59-61-79',
                'photo': 'images/employees/stankevich-anatolij-ivanovich.jpg'
            },
            {
                'name': 'Павлюкова Виктория Петровна',
                'position': 'Начальник ОМТС',
                'email': 'omts@gomelzlin.by',
                'phone': '+375-232-59-62-33',
                'photo': 'images/employees/pavlyukova-viktoriya-petrovna.jpg'
            },
            {
                'name': 'Какора Надежда Адамовна',
                'position': 'Главный экономист',
                'email': 'kakora@gomelzlin.by',
                'phone': '+375-232-59-68-77',
                'photo': 'images/employees/kakora-nadezhda-adamovna.jpg'
            },
            {
                'name': 'Камко Татьяна Михайловна',
                'position': 'Главный бухгалтер',
                'email': 'buh@gomelzlin.by',
                'phone': '+375-232-59-69-64',
                'photo': 'images/employees/kamko-tatsyana-mihajlovna.jpg'
            },
            {
                'name': 'Мосензовенко Александр Викторович',
                'position': 'Главный технолог',
                'email': 'ogt@gomelzlin.by',
                'phone': '+375-232-59-61-86',
                'photo': 'images/employees/mosenzovenko-aleksandr-viktorovich.jpg'
            },
            {
                'name': 'Гасымов Владислав Гисматович',
                'position': 'Начальник отдела кадров',
                'email': 'ok@gomelzlin.by',
                'phone': '+375-232-59-67-97',
                'photo': 'images/employees/gasymov-vladislav-gismatovich.jpg'
            },
            {
                'name': 'Трашков Андрей Владимирович',
                'position': 'Начальник отдела продаж',
                'email': 'op@gomelzlin.by',
                'phone': '+375-232-59-65-14',
                'photo': 'images/employees/trashkov-andrej-vladimirovich.jpg'
            },
            {
                'name': 'Швайба Екатерина Васильевна',
                'position': 'Начальник центра маркетинговых коммуникаций',
                'email': 'om@gomelzlin.by',
                'phone': '+375-232-59-62-40',
                'photo': 'images/employees/shvajba-ekaterina-vasilevna.jpg'
            },
            {
                'name': 'Герасименко Юрий Валерьевич',
                'position': 'Начальник транспортного управления',
                'email': 'tto@gomelzlin.by',
                'phone': '+375-232-59-60-80',
                'photo': 'images/employees/gerasimenko-yurij-valerevich.jpg'
            },
            {
                'name': 'Давыдова Тамара Николаевна',
                'position': 'Начальник юридического отдела',
                'email': 'tmdavidova@gomelzlin.by',
                'phone': '+375-232-59-69-16',
                'photo': 'images/employees/davydova-tamara-nikolaevna.jpg'
            }
        ]
        return context

class PartnersView(TemplateView):
    template_name = 'company/partners.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Партнеры'
        context['partners'] = [
            {
                'name': 'ОАО "БЕЛАЗ"',
                'description': 'Ведущий производитель карьерной техники в мире',
                'website': 'https://belaz.by',
                'logo': 'images/partners/belaz.jpg'
            },
            {
                'name': 'ОАО "МТЗ"',
                'description': 'Минский тракторный завод - производитель сельхозтехники',
                'website': 'https://mtz.by',
                'logo': 'images/partners/mtz.jpg'
            },
            {
                'name': 'ОАО "МАЗ"',
                'description': 'Минский автомобильный завод',
                'website': 'https://maz.by',
                'logo': 'images/partners/maz.jpg'
            }
        ]
        return context

class PoliciesView(TemplateView):
    template_name = 'company/policies.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Политики компании'
        return context

class HRPolicyView(TemplateView):
    """Кадровая политика"""
    template_name = 'company/hr_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Кадровая политика'
        return context

class SocialPolicyView(TemplateView):
    """Социальная политика"""
    template_name = 'company/social_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Социальная политика'
        context['social_tasks'] = [
            {
                'title': 'ЗАЩИТА ОКРУЖАЮЩЕЙ СРЕДЫ',
                'description': 'Мы заботимся об экологии и используем современные технологии для минимизации воздействия на окружающую среду.',
                'icon': 'fas fa-leaf'
            },
            {
                'title': 'ОБЕСПЕЧЕНИЕ БЕЗОПАСНОСТИ СОТРУДНИКОВ',
                'description': 'Безопасность труда - наш приоритет. Мы обеспечиваем современные средства защиты и регулярное обучение персонала.',
                'icon': 'fas fa-hard-hat'
            },
            {
                'title': 'ОБРАЗОВАТЕЛЬНЫЕ ПРОЕКТЫ ОАО "ГЗЛиН"',
                'description': 'Поддержка образования и развития профессиональных навыков сотрудников и молодых специалистов.',
                'icon': 'fas fa-graduation-cap'
            }
        ]
        return context