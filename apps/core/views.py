from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.http import Http404
from django.core.paginator import Paginator
from django.utils import timezone
from .models import News
from django.conf import settings
from django.http import JsonResponse

def test_404(request):
    raise Http404("Тест кастомной 404")

class HomeView(TemplateView):
    """Главная страница с новостями и популярными категориями"""
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ОАО "ГЗЛиН" - Главная страница'
        
        try:
            context['featured_news'] = News.get_featured(limit=3)
        except:
            context['featured_news'] = []
        
        featured_categories = []
        try:
            from apps.catalog.models import Category
            
            categories = Category.objects.filter(is_featured=True, is_active=True)
            
            for category in categories: 
                product_count = self.count_products_in_category(category)
                
                featured_categories.append({
                    'id': category.id,
                    'name': category.name,
                    'description': category.description or '',
                    'get_absolute_url': category.get_absolute_url(),
                    'product_count': product_count
                })
                
        except Exception as e:
            print(f"Ошибка загрузки популярных категорий: {e}")
        
        context['featured_categories'] = featured_categories
        
        try:
            from apps.catalog.models import Product
            context['featured_products'] = Product.objects.filter(
                is_active=True,
                is_published=True,
                is_featured=True
            ).select_related('category')[:4]
        except:
            context['featured_products'] = []
        
        return context
    
    def count_products_in_category(self, category):
        """Подсчитывает количество товаров в категории и всех её подкатегориях"""
        try:
            count = category.products.filter(is_active=True, is_published=True).count()
            
            for child in category.children.filter(is_active=True):
                count += self.count_products_in_category(child)
            
            return count
        except Exception as e:
            print(f"⚠️ Ошибка подсчета товаров для категории {category.name}: {e}")
            return 0


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
        
        session_key = f'news_viewed_{obj.pk}'
        if not self.request.session.get(session_key, False):
            obj.increment_views()
            self.request.session[session_key] = True
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        
        context['related_news'] = News.get_published().exclude(
            pk=self.object.pk
        ).order_by('-published_at')[:3]
        
        return context

def test_api_key(request):
    """Тестирование API ключа"""
    return JsonResponse({
        'yandex_api_key': getattr(settings, 'YANDEX_MAPS_API_KEY', 'NOT_SET'),
        'key_length': len(getattr(settings, 'YANDEX_MAPS_API_KEY', '')),
        'is_set': bool(getattr(settings, 'YANDEX_MAPS_API_KEY', ''))
    })