# apps/catalog/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, F
from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Category, Product


class ProductListView(TemplateView):
    """Главная страница каталога с категориями"""
    template_name = 'catalog/product_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Каталог товаров'
        
        # Получаем категории, если модель существует
        if Category:
            categories = Category.objects.filter(
                parent__isnull=True,
                is_active=True
            ).prefetch_related('children')[:6]
            
            categories_with_counts = []
            for category in categories:
                if hasattr(category, 'slug') and category.slug:
                    categories_with_counts.append({
                        'id': category.id,
                        'name': category.name,
                        'description': getattr(category, 'description', ''),
                        'slug': category.slug,
                        'absolute_url': category.get_absolute_url() if hasattr(category, 'get_absolute_url') else '#',
                        'total_products': 0,
                    })
            
            context['categories_with_counts'] = categories_with_counts
        else:
            context['categories_with_counts'] = []
        
        # Получаем товары, если модель существует
        if Product:
            context['featured_products'] = Product.objects.filter(
                is_active=True,
                is_published=True
            )[:6]
        else:
            context['featured_products'] = []
        
        return context

class CategoryDetailView(TemplateView):
    """Детальная страница категории"""
    template_name = 'catalog/category_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if Category:
            category = get_object_or_404(Category, slug=kwargs['slug'], is_active=True)
            context['category'] = category
            context['title'] = category.name
            
            # Проверяем наличие подкатегорий
            has_subcategories = category.children.filter(is_active=True).exists()
            context['show_subcategories'] = has_subcategories
            
            if has_subcategories:
                context['subcategories'] = category.children.filter(is_active=True)
            else:
                # Показываем товары
                if Product:
                    products = category.products.filter(is_active=True, is_published=True)
                    context['products'] = products
                else:
                    context['products'] = []
        else:
            context['category'] = None
            context['title'] = 'Категория не найдена'
        
        return context

class ProductDetailView(DetailView):
    """Детальная страница товара"""
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        if Product:
            return Product.objects.filter(is_active=True, is_published=True)
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['title'] = self.object.name
        return context

class ProductSearchView(ListView):
    """Поиск товаров"""
    template_name = 'catalog/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        if not Product:
            return Product.objects.none()
        
        queryset = Product.objects.filter(is_active=True, is_published=True)
        
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['title'] = 'Поиск товаров'
        return context


def quick_search_ajax(request):
    """Быстрый поиск для автокомплита"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2 or not Product:
        return JsonResponse({'results': []})
    
    # Поиск товаров
    products = Product.objects.filter(
        Q(name__icontains=query),
        is_active=True,
        is_published=True
    ).values('id', 'name', 'price')[:10]
    
    # Поиск категорий
    categories = []
    if Category:
        categories = Category.objects.filter(
            name__icontains=query,
            is_active=True
        ).values('id', 'name', 'slug')[:5]
    
    results = {
        'products': list(products),
        'categories': list(categories)
    }
    
    return JsonResponse({'results': results})

# Представления для главной страницы

class HomeView(TemplateView):
    """Главная страница с категориями"""
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Популярные категории для главной страницы
        featured_categories = []
        categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True,
            is_featured=True
        ).order_by('sort_order', 'name')[:6]  # Показываем только 6 основных
        
        for category in categories:
            if category.slug:  # Только категории с валидным slug
                product_count = self.count_products_in_category(category)
                featured_categories.append({
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'get_absolute_url': category.get_absolute_url(),
                    'product_count': product_count
                })
        
        context['featured_categories'] = featured_categories
        
        # Популярные товары
        context['featured_products'] = Product.objects.filter(
            is_active=True,
            is_published=True,
            is_featured=True
        ).select_related('category')[:4]
        
        return context
    
    def count_products_in_category(self, category):
        """Подсчитывает количество товаров в категории и всех её подкатегориях"""
        count = category.products.filter(is_active=True, is_published=True).count()
        
        # Добавляем товары из подкатегорий
        for child in category.children.filter(is_active=True):
            count += self.count_products_in_category(child)
        
        return count