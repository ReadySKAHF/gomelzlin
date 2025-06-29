from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import Http404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import News

class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ОАО "ГЗЛиН" - Главная страница'
        
        # Получаем рекомендуемые новости для главной страницы
        context['featured_news'] = News.get_featured(limit=3)
        
        return context

class ContactsView(TemplateView):
    template_name = 'pages/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['company_info'] = {
            'phone': '+375 232 12-34-56',
            'email': 'info@gomelzlin.by',
            'address': '246000, г. Гомель, ул. Промышленная, 15',
            'working_hours': 'Пн-Пт: 8:00-17:00\nСб-Вс: выходной'
        }
        return context
    
class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ОАО "ГЗЛиН" - Главная страница'
        
        # Получаем рекомендуемые новости для главной страницы
        context['featured_news'] = News.get_featured(limit=3)
        
        return context


class NewsListView(ListView):
    """Список всех новостей"""
    model = News
    template_name = 'news/news_list.html'
    context_object_name = 'news_list'
    paginate_by = 12
    
    def get_queryset(self):
        return News.get_published().select_related('author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Новости компании'
        return context


class NewsDetailView(DetailView):
    """Детальный просмотр новости"""
    model = News
    template_name = 'news/news_detail.html'
    context_object_name = 'news'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return News.get_published().select_related('author')
    
    def get_object(self, queryset=None):
        """Получаем объект и увеличиваем счетчик просмотров"""
        obj = super().get_object(queryset)
        
        # Увеличиваем счетчик просмотров (один раз за сессию)
        session_key = f'news_viewed_{obj.pk}'
        if not self.request.session.get(session_key, False):
            obj.increment_views()
            self.request.session[session_key] = True
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        
        # Получаем похожие новости (последние 3, исключая текущую)
        context['related_news'] = News.get_published().exclude(
            pk=self.object.pk
        ).order_by('-published_at')[:3]
        
        return context


class ContactsView(TemplateView):
    template_name = 'pages/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['company_info'] = {
            'phone': '+375 232 12-34-56',
            'email': 'info@gomelzlin.by',
            'address': '246000, г. Гомель, ул. Промышленная, 15',
            'working_hours': 'Пн-Пт: 8:00-17:00\nСб-Вс: выходной'
        }
        return context