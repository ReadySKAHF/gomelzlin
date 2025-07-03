from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Leader, Partner

class AboutView(TemplateView):
    template_name = 'company/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'О компании'
        
        context['partners'] = Partner.objects.filter(
            is_public=True,
            is_active=True
        ).order_by('-is_featured', 'sort_order', 'name')
        
        context['leaders'] = Leader.objects.filter(
            is_public=True, 
            is_active=True
        ).order_by('sort_order', 'position_type', 'last_name')
        
        return context

class LeadershipView(TemplateView):
    template_name = 'company/leadership.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Руководство'
        
        context['leaders'] = Leader.objects.filter(
            is_public=True,
            is_active=True
        ).order_by('sort_order', 'position_type', 'last_name')
        
        return context

class PartnersView(TemplateView):
    template_name = 'company/partners.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Партнёры'
        
        context['partners'] = Partner.objects.filter(
            is_public=True,
            is_active=True
        ).order_by('-is_featured', 'sort_order', 'name')
        
        context['featured_partners'] = context['partners'].filter(is_featured=True)
        context['regular_partners'] = context['partners'].filter(is_featured=False)
        
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