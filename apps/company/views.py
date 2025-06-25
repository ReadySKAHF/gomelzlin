from django.shortcuts import render
from django.views.generic import TemplateView

class AboutView(TemplateView):
    template_name = 'company/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О компании'
        return context

class LeadershipView(TemplateView):
    template_name = 'company/leadership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Руководство'
        context['leaders'] = [
            {
                'name': 'Иванов Иван Иванович',
                'position': 'Генеральный директор',
                'email': 'director@gomelzlin.by',
                'phone': '+375 232 12-34-56',
                'photo': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200&h=200&fit=crop&crop=face'
            },
            {
                'name': 'Петрова Анна Сергеевна',
                'position': 'Технический директор',
                'email': 'tech@gomelzlin.by',
                'phone': '+375 232 12-34-57',
                'photo': 'https://images.unsplash.com/photo-1494790108755-2616b612b3e4?w=200&h=200&fit=crop&crop=face'
            },
            {
                'name': 'Сидоров Петр Алексеевич',
                'position': 'Коммерческий директор',
                'email': 'sales@gomelzlin.by',
                'phone': '+375 232 12-34-58',
                'photo': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop&crop=face'
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
                'description': 'Ведущий производитель карьерной техники',
                'website': 'https://belaz.by',
                'logo': 'https://via.placeholder.com/150x100?text=BELAZ'
            },
            {
                'name': 'ОАО "МТЗ"',
                'description': 'Минский тракторный завод',
                'website': 'https://mtz.by',
                'logo': 'https://via.placeholder.com/150x100?text=MTZ'
            },
            {
                'name': 'ОАО "МАЗ"',
                'description': 'Минский автомобильный завод',
                'website': 'https://maz.by',
                'logo': 'https://via.placeholder.com/150x100?text=MAZ'
            }
        ]
        return context

class RequisitesView(TemplateView):
    """Страница реквизитов компании"""
    template_name = 'company/requisites.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Реквизиты'
        context['requisites'] = {
            'full_name': 'Открытое акционерное общество "Гомельский завод литейных изделий"',
            'short_name': 'ОАО "ГЗЛиН"',
            'unp': '400000000',
            'okpo': '12345678',
            'legal_address': '246000, Республика Беларусь, г. Гомель, ул. Промышленная, 15',
            'postal_address': '246000, Республика Беларусь, г. Гомель, ул. Промышленная, 15',
            'phone': '+375 (232) 12-34-56',
            'fax': '+375 (232) 12-34-57',
            'email': 'info@gomelzlin.by',
            'website': 'www.gomelzlin.by',
            'bank_details': {
                'bank_name': 'ОАО "Белагропромбанк"',
                'bank_code': '153001749',
                'account_byn': 'BY12 1530 0000 0000 0000 1234',
                'account_usd': 'BY12 1530 0000 0000 0000 5678',
                'account_eur': 'BY12 1530 0000 0000 0000 9012'
            },
            'director': 'Иванов Иван Иванович',
            'chief_accountant': 'Петрова Анна Сергеевна'
        }
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