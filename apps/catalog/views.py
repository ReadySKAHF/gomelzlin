# apps/catalog/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, F, Exists, OuterRef
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
        
        # Получаем только родительские категории (без parent)
        main_categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children', 'products').order_by('sort_order', 'name')
        
        categories_with_counts = []
        for category in main_categories:
            # Подсчитываем общее количество товаров в категории и подкатегориях
            total_products = self.get_category_product_count(category)
            
            # Определяем изображение категории
            category_image = self.get_category_image(category.name)
            
            categories_with_counts.append({
                'id': category.id,
                'name': category.name,
                'description': getattr(category, 'description', ''),
                'slug': category.slug,
                'image': category_image,
                'total_products': total_products,
                'absolute_url': category.get_absolute_url() if hasattr(category, 'get_absolute_url') else f'/catalog/category/{category.slug}/',
            })
        
        context['categories'] = categories_with_counts
        
        # Получаем рекомендуемые товары
        try:
            featured_products = Product.objects.filter(
                is_active=True,
                is_published=True,
                is_featured=True
            ).select_related('category')[:6]
            context['featured_products'] = featured_products
        except:
            context['featured_products'] = []
        
        return context
    
    def get_category_product_count(self, category):
        """Подсчитывает общее количество товаров в категории и всех подкатегориях"""
        count = 0
        try:
            # Товары в самой категории
            count += category.products.filter(is_active=True, is_published=True).count()
            
            # Товары в подкатегориях
            for subcategory in category.children.filter(is_active=True):
                count += subcategory.products.filter(is_active=True, is_published=True).count()
        except:
            pass
        return count
    
    def get_category_image(self, category_name):
        """Возвращает путь к изображению категории"""
        category_images = {
            'Зерноуборочная техника': 'static/images/categories/grain_harvesting.jpg',
            'Кормоуборочная техника': 'images/categories/feed_harvesting.jpg',
            'Картофелеуборочная техника': 'images/categories/potato_harvesting.jpg',
            'Метизная продукция': 'images/categories/hardware.jpg',
            'Прочая техника': 'images/categories/other_equipment.jpg',
            'Бункеры-перегрузчики': 'images/categories/bunkers.jpg',
            'Новинки': 'images/categories/new_products.jpg',
            'Прочие товары, работы и услуги': 'images/categories/services.jpg',
            'Режущие системы жаток': 'images/categories/cutting_systems.jpg',
            'Самоходные носилки': 'images/categories/self_propelled.jpg',
        }
        return category_images.get(category_name, 'images/categories/default.jpg')

class CategoryDetailView(TemplateView):
    """Детальная страница категории"""
    template_name = 'catalog/category_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем категорию по slug
        category = get_object_or_404(Category, slug=kwargs['slug'], is_active=True)
        context['category'] = category
        context['title'] = category.name
        
        # Проверяем наличие подкатегорий
        subcategories = category.children.filter(is_active=True).order_by('sort_order', 'name')
        
        if subcategories.exists():
            # Есть подкатегории - показываем их
            context['show_subcategories'] = True
            subcategories_with_counts = []
            
            for subcategory in subcategories:
                product_count = subcategory.products.filter(is_active=True, is_published=True).count()
                subcategories_with_counts.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'description': subcategory.description,
                    'slug': subcategory.slug,
                    'product_count': product_count,
                    'absolute_url': subcategory.get_absolute_url()
                })
            
            context['subcategories'] = subcategories_with_counts
        else:
            # Нет подкатегорий - показываем товары
            context['show_subcategories'] = False
            
            # Получаем параметры отображения
            view_type = self.request.GET.get('view', 'grid')  # grid или list
            context['view_type'] = view_type
            
            # Получаем товары категории
            products = category.products.filter(
                is_active=True, 
                is_published=True
            ).order_by('name')
            
            # Пагинация
            paginator = Paginator(products, 12)
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['products'] = page_obj
            context['paginator'] = paginator
        
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_active=True, 
            is_published=True
        ).select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        context['title'] = product.name
        
        # Похожие товары из той же категории
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True,
            is_published=True
        ).exclude(id=product.id)[:4]
        
        context['related_products'] = related_products
        
        return context

class ProductSearchView(ListView):
    """Поиск товаров"""
    template_name = 'catalog/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) | 
                Q(description__icontains=query) |
                Q(article__icontains=query),
                is_active=True,
                is_published=True
            ).select_related('category')
        return Product.objects.none()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        context['title'] = f'Поиск: {context["query"]}'
        return context


def quick_search_ajax(request):
    """AJAX быстрый поиск"""
    query = request.GET.get('q', '')
    results = []
    
    if len(query) >= 2:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(article__icontains=query),
            is_active=True,
            is_published=True
        )[:5]
        
        for product in products:
            results.append({
                'name': product.name,
                'article': product.article,
                'price': str(product.price),
                'url': product.get_absolute_url(),
                'image': product.image.url if product.image else None
            })
    
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