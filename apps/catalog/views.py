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
        
        # Получаем основные категории с количеством товаров
        categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children', 'products').order_by('sort_order', 'name')
        
        categories_with_counts = []
        for category in categories:
            # Пропускаем категории с пустыми slug'ами
            if not category.slug:
                continue
                
            # Считаем товары в категории и всех подкатегориях
            total_products = self.count_products_in_category(category)
            
            try:
                # Безопасное получение URL
                absolute_url = category.get_absolute_url()
            except:
                # Если не удается создать URL, используем заглушку
                absolute_url = '#'
            
            categories_with_counts.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'slug': category.slug,
                'absolute_url': absolute_url,
                'total_products': total_products,
                'is_featured': category.is_featured,
                'sort_order': category.sort_order
            })
        
        context['categories_with_counts'] = categories_with_counts
        
        # Получаем все категории для фильтра поиска
        context['all_categories'] = Category.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Получаем популярные товары
        context['featured_products'] = Product.objects.filter(
            is_active=True,
            is_published=True,
            is_featured=True
        ).select_related('category')[:6]
        
        return context
    
    def count_products_in_category(self, category):
        """Подсчитывает количество товаров в категории и всех её подкатегориях"""
        count = category.products.filter(is_active=True, is_published=True).count()
        
        # Добавляем товары из подкатегорий
        for child in category.children.filter(is_active=True):
            count += self.count_products_in_category(child)
        
        return count


class CategoryDetailView(TemplateView):
    """Детальная страница категории с подкатегориями или товарами"""
    template_name = 'catalog/category_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем категорию по slug
        category = get_object_or_404(
            Category.objects.prefetch_related('children', 'products'),
            slug=kwargs['slug'],
            is_active=True
        )
        
        context['category'] = category
        context['title'] = category.name
        
        # Определяем, показывать подкатегории или товары
        has_subcategories = category.children.filter(is_active=True).exists()
        
        if has_subcategories:
            # Показываем подкатегории
            context['show_subcategories'] = True
            subcategories = []
            
            for subcategory in category.children.filter(is_active=True).order_by('sort_order', 'name'):
                product_count = subcategory.products.filter(is_active=True, is_published=True).count()
                subcategories.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'description': subcategory.description,
                    'slug': subcategory.slug,
                    'image': subcategory.image if subcategory.image else None,
                    'product_count': product_count,
                    'get_absolute_url': subcategory.get_absolute_url() if subcategory.slug else '#'
                })
            
            context['subcategories'] = subcategories
        else:
            # Показываем товары
            context['show_subcategories'] = False
            
            # Получаем товары с фильтрацией и пагинацией
            products = category.products.filter(
                is_active=True,
                is_published=True
            ).select_related('category').order_by('name')
            
            # Поиск по товарам в категории
            search_query = self.request.GET.get('search', '').strip()
            if search_query:
                products = products.filter(
                    Q(name__icontains=search_query) |
                    Q(article__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            # Сортировка товаров
            sort_by = self.request.GET.get('sort', 'name')
            if sort_by == 'price_asc':
                products = products.order_by('price')
            elif sort_by == 'price_desc':
                products = products.order_by('-price')
            elif sort_by == 'name_desc':
                products = products.order_by('-name')
            else:  # name_asc или по умолчанию
                products = products.order_by('name')
            
            # Пагинация
            paginator = Paginator(products, 12)  # 12 товаров на страницу
            page_number = self.request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            
            context['products'] = page_obj
            context['search_query'] = search_query
            context['current_sort'] = sort_by
            
            # Параметры отображения (плитки или список)
            context['view_mode'] = self.request.GET.get('view', 'grid')  # grid или list
        
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name
        
        # Похожие товары из той же категории
        related_products = Product.objects.filter(
            category=self.object.category,
            is_active=True,
            is_published=True
        ).exclude(
            id=self.object.id
        ).select_related('category')[:4]
        
        context['related_products'] = related_products
        
        return context


class ProductSearchView(ListView):
    """Поиск товаров"""
    model = Product
    template_name = 'catalog/search_results.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(
            is_active=True,
            is_published=True
        ).select_related('category')
        
        # Поисковый запрос
        search_query = self.request.GET.get('search', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(article__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Фильтр по категории
        category_id = self.request.GET.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id, is_active=True)
                # Включаем товары из подкатегорий
                category_ids = [category.id]
                category_ids.extend(
                    category.children.filter(is_active=True).values_list('id', flat=True)
                )
                queryset = queryset.filter(category__id__in=category_ids)
            except (Category.DoesNotExist, ValueError):
                pass
        
        # Фильтр по цене
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except ValueError:
                pass
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except ValueError:
                pass
        
        # Сортировка
        sort_by = self.request.GET.get('sort', 'name')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'name_desc':
            queryset = queryset.order_by('-name')
        else:
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        search_query = self.request.GET.get('search', '').strip()
        context['search_query'] = search_query
        context['title'] = f'Поиск: {search_query}' if search_query else 'Поиск товаров'
        
        # Параметры для формы поиска
        context['selected_category'] = self.request.GET.get('category', '')
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['current_sort'] = self.request.GET.get('sort', 'name')
        context['view_mode'] = self.request.GET.get('view', 'grid')
        
        # Все категории для фильтра
        context['all_categories'] = Category.objects.filter(
            is_active=True
        ).order_by('name')
        
        # Статистика поиска
        total_results = context['paginator'].count if context.get('paginator') else 0
        context['total_results'] = total_results
        
        return context


# Дополнительные view-функции для AJAX-запросов

def category_products_ajax(request, category_id):
    """AJAX-получение товаров категории"""
    try:
        category = Category.objects.get(id=category_id, is_active=True)
        products = category.products.filter(
            is_active=True,
            is_published=True
        ).values('id', 'name', 'price', 'article')[:10]
        
        return JsonResponse({
            'success': True,
            'products': list(products),
            'category_name': category.name
        })
    except Category.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Категория не найдена'
        })


def quick_search_ajax(request):
    """Быстрый поиск для автокомплита"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    # Поиск товаров
    products = Product.objects.filter(
        Q(name__icontains=query) | Q(article__icontains=query),
        is_active=True,
        is_published=True
    ).values('id', 'name', 'article', 'price')[:10]
    
    # Поиск категорий
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