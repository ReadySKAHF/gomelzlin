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
                'website': 'https://belaz.by'
            },
            {
                'name': 'ОАО "МТЗ"',
                'description': 'Минский тракторный завод',
                'website': 'https://mtz.by'
            },
            {
                'name': 'ОАО "МАЗ"',
                'description': 'Минский автомобильный завод',
                'website': 'https://maz.by'
            }
        ]
        return context

class PoliciesView(TemplateView):
    template_name = 'company/policies.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Политики компании'
        return context