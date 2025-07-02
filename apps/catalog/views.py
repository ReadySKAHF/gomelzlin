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
            
            # Определяем изображение категории (эмодзи)
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
        
        # ИСПРАВЛЕНО: Завершаем присвоение categories
        context['categories'] = categories_with_counts
        
        # Получаем рекомендуемые товары
        try:
            featured_products = Product.objects.filter(
                is_active=True,
                is_published=True,
                is_featured=True
            ).select_related('category')[:6]
            context['featured_products'] = featured_products
        except Exception as e:
            print(f"Ошибка получения рекомендуемых товаров: {e}")
            context['featured_products'] = []
        
        return context
    
    def get_category_product_count(self, category):
        """Подсчитывает количество товаров в категории и подкатегориях"""
        try:
            # Товары в самой категории
            count = category.products.filter(is_active=True, is_published=True).count()
            
            # Товары в подкатегориях
            for child in category.children.filter(is_active=True):
                count += child.products.filter(is_active=True, is_published=True).count()
            
            return count
        except Exception:
            return 0
    
    def get_category_image(self, category_name):
        """Возвращает эмодзи для категории"""
        emoji_map = {
            'Зерноуборочная техника': '🌾',
            'Кормоуборочная техника': '🚜',
            'Картофелеуборочная техника': '🥔',
            'Метизная продукция': '🔩',
            'Прочая техника': '⚙️',
            'Бункеры-перегрузчики': '📦',
            'Новинки': '✨',
            'Прочие товары, работы и услуги': '🛠️',
            'Режущие системы жаток': '⚔️',
            'Самоходные носилки': '🚚',
        }
        return emoji_map.get(category_name, '🏭')


class CategoryDetailView(TemplateView):
    """Детальная страница категории"""
    template_name = 'catalog/category_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        
        try:
            category = get_object_or_404(Category, slug=slug, is_active=True)
            context['category'] = category
            context['title'] = category.name
            
            # Получаем подкатегории
            subcategories = category.children.filter(is_active=True).order_by('sort_order', 'name')
            
            # Получаем товары категории
            products = Product.objects.filter(
                category=category,
                is_active=True,
                is_published=True
            ).select_related('category').order_by('name')
            
            context['subcategories'] = subcategories
            context['products'] = products
            context['has_subcategories'] = subcategories.exists()
            
            # Добавляем информацию о количестве товаров для подкатегорий
            subcategories_with_counts = []
            for subcat in subcategories:
                subcategories_with_counts.append({
                    'category': subcat,
                    'product_count': subcat.products.filter(is_active=True, is_published=True).count()
                })
            context['subcategories_with_counts'] = subcategories_with_counts
            
            # Добавляем тип отображения (плитка/список)
            view_type = self.request.GET.get('view', 'grid')
            context['view_type'] = view_type
            
        except Category.DoesNotExist:
            context['category'] = None
            context['error'] = 'Категория не найдена'
            
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    
    def get_queryset(self):
        return Product.objects.filter(
            is_active=True,
            is_published=True
        ).select_related('category')
    
    def get_object(self):
        obj = super().get_object()
        # Увеличиваем счетчик просмотров
        if hasattr(obj, 'increment_views'):
            obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['title'] = product.name
        
        # Получаем похожие товары из той же категории
        similar_products = Product.objects.filter(
            category=product.category,
            is_active=True,
            is_published=True
        ).exclude(id=product.id).select_related('category')[:4]
        
        context['similar_products'] = similar_products
        
        # Проверяем, есть ли изображения
        if hasattr(product, 'images'):
            context['product_images'] = product.images.filter(is_active=True).order_by('sort_order')
        
        return context

class ProductSearchView(ListView):
    """Поиск товаров"""
    model = Product
    template_name = 'catalog/product_search.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        
        if not query:
            return Product.objects.none()
        
        # Поиск по названию, описанию и артикулу
        queryset = Product.objects.filter(
            Q(name__icontains=query) |
            Q(short_description__icontains=query) |
            Q(description__icontains=query) |
            Q(article__icontains=query),
            is_active=True,
            is_published=True
        ).select_related('category').distinct()
        
        # Сортировка по релевантности
        queryset = queryset.order_by('-is_featured', 'name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        context['title'] = f'Поиск: {query}' if query else 'Поиск товаров'
        
        # Добавляем тип отображения
        view_type = self.request.GET.get('view', 'grid')
        context['view_type'] = view_type
        
        # Добавляем категории, которые соответствуют поисковому запросу
        if query:
            matching_categories = Category.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query),
                is_active=True
            ).order_by('name')[:5]
            context['matching_categories'] = matching_categories
        
        return context


def quick_search_ajax(request):
    """AJAX поиск для автокомплита с поддержкой категорий и товаров"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    # Поиск по категориям
    categories = Category.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).order_by('name')[:5]
    
    for category in categories:
        # Подсчет товаров в категории
        product_count = category.products.filter(is_active=True, is_published=True).count()
        
        # Добавляем товары из подкатегорий
        for child in category.children.filter(is_active=True):
            product_count += child.products.filter(is_active=True, is_published=True).count()
        
        results.append({
            'id': category.id,
            'name': category.name,
            'type': 'category',
            'article': None,
            'category_name': None,
            'product_count': product_count,
            'url': category.get_absolute_url() if hasattr(category, 'get_absolute_url') else f'/catalog/category/{category.slug}/',
        })
    
    # Поиск по товарам
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(article__icontains=query) |
        Q(short_description__icontains=query),
        is_active=True,
        is_published=True
    ).select_related('category').order_by('-is_featured', 'name')[:8]
    
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'type': 'product',
            'article': product.article,
            'category_name': product.category.name if product.category else None,
            'price': str(product.price) if hasattr(product, 'price') and product.price else None,
            'url': product.get_absolute_url() if hasattr(product, 'get_absolute_url') else f'/catalog/product/{product.slug}/',
        })
    
    # Ограничиваем общее количество результатов
    results = results[:10]
    
    return JsonResponse({'results': results})


def category_search_ajax(request):
    """AJAX поиск только по категориям"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    categories = Category.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True
    ).order_by('name')[:8]
    
    results = []
    for category in categories:
        # Подсчет товаров в категории
        product_count = category.products.filter(is_active=True, is_published=True).count()
        
        # Добавляем товары из подкатегорий
        for child in category.children.filter(is_active=True):
            product_count += child.products.filter(is_active=True, is_published=True).count()
        
        results.append({
            'id': category.id,
            'name': category.name,
            'description': category.description[:100] if category.description else '',
            'product_count': product_count,
            'url': category.get_absolute_url() if hasattr(category, 'get_absolute_url') else f'/catalog/category/{category.slug}/',
            'has_subcategories': category.children.filter(is_active=True).exists(),
        })
    
    return JsonResponse({'results': results})


def product_search_ajax(request):
    """AJAX поиск только по товарам"""
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category', None)
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Базовый запрос
    queryset = Product.objects.filter(
        Q(name__icontains=query) |
        Q(article__icontains=query) |
        Q(short_description__icontains=query),
        is_active=True,
        is_published=True
    ).select_related('category')
    
    # Фильтр по категории
    if category_id:
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            # Включаем товары из данной категории и всех её подкатегорий
            category_ids = [category.id]
            category_ids.extend(category.children.filter(is_active=True).values_list('id', flat=True))
            queryset = queryset.filter(category_id__in=category_ids)
        except Category.DoesNotExist:
            pass
    
    products = queryset.order_by('-is_featured', 'name')[:10]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'article': product.article,
            'category_name': product.category.name if product.category else None,
            'price': str(product.price) if hasattr(product, 'price') and product.price else None,
            'in_stock': product.stock_quantity > 0 if hasattr(product, 'stock_quantity') else True,
            'url': product.get_absolute_url() if hasattr(product, 'get_absolute_url') else f'/catalog/product/{product.slug}/',
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