# apps/catalog/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q, Count, F
from django.db import models
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Category, Product

# Импортируем формы только если они существуют
try:
    from .forms import ProductSearchForm, QuickSearchForm, ProductFilterForm
except ImportError:
    # Создаем заглушки если форм нет
    class ProductSearchForm:
        def __init__(self, *args, **kwargs):
            pass
        def is_valid(self):
            return False
        def cleaned_data(self):
            return {}
    
    class QuickSearchForm:
        def __init__(self, *args, **kwargs):
            pass
    
    class ProductFilterForm:
        def __init__(self, *args, **kwargs):
            pass
        def is_valid(self):
            return False
        def cleaned_data(self):
            return {}


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
        ).prefetch_related('children', 'products')
        
        categories_with_counts = []
        for category in categories:
            # Считаем товары в категории и всех подкатегориях
            total_products = self.count_products_in_category(category)
            
            categories_with_counts.append({
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'slug': category.slug,
                'product_count': total_products,
                'image': category.image.url if category.image else None,
                'is_featured': category.is_featured,
                'get_absolute_url': category.get_absolute_url()
            })
        
        context['categories'] = categories_with_counts
        
        # Рекомендуемые товары
        try:
            featured_products = Product.objects.filter(
                is_active=True,
                is_published=True,
                is_featured=True
            ).select_related('category')[:8]
            context['featured_products'] = featured_products
        except:
            context['featured_products'] = []
        
        # Новинки
        try:
            new_products = Product.objects.filter(
                is_active=True,
                is_published=True
            ).select_related('category').order_by('-created_at')[:6]
            context['new_products'] = new_products
        except:
            context['new_products'] = []
        
        # Форма быстрого поиска
        context['quick_search_form'] = QuickSearchForm()
        
        return context
    
    def count_products_in_category(self, category):
        """Подсчитывает количество товаров в категории и всех её подкатегориях"""
        try:
            count = category.products.filter(is_active=True, is_published=True).count()
            
            # Добавляем товары из подкатегорий
            for child in category.children.filter(is_active=True):
                count += self.count_products_in_category(child)
            
            return count
        except:
            return 0


class CategoryDetailView(TemplateView):
    """Детальная страница категории с фильтрацией"""
    template_name = 'catalog/category_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        
        # Получаем категорию
        category = get_object_or_404(Category, slug=slug, is_active=True)
        context['category'] = category
        context['title'] = category.name
        
        # Если у категории есть подкатегории, показываем их
        if category.children.filter(is_active=True).exists():
            subcategories = category.children.filter(is_active=True)
            subcategories_with_counts = []
            
            for subcategory in subcategories:
                try:
                    product_count = subcategory.products.filter(
                        is_active=True, 
                        is_published=True
                    ).count()
                except:
                    product_count = 0
                    
                subcategories_with_counts.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'description': subcategory.description,
                    'slug': subcategory.slug,
                    'product_count': product_count,
                    'image': subcategory.image.url if subcategory.image else None,
                    'get_absolute_url': subcategory.get_absolute_url()
                })
            
            context['subcategories'] = subcategories_with_counts
            context['show_subcategories'] = True
        else:
            # Показываем товары категории с фильтрацией
            filter_form = ProductFilterForm(self.request.GET)
            try:
                products_queryset = category.products.filter(
                    is_active=True, 
                    is_published=True
                )
            except:
                products_queryset = Product.objects.none()
            
            # Применяем фильтры
            if filter_form.is_valid():
                price_from = filter_form.cleaned_data.get('price_from')
                if price_from:
                    products_queryset = products_queryset.filter(price__gte=price_from)
                
                price_to = filter_form.cleaned_data.get('price_to')
                if price_to:
                    products_queryset = products_queryset.filter(price__lte=price_to)
                
                in_stock = filter_form.cleaned_data.get('in_stock')
                if in_stock:
                    products_queryset = products_queryset.filter(stock_quantity__gt=0)
                
                sort = filter_form.cleaned_data.get('sort')
                if sort:
                    products_queryset = products_queryset.order_by(sort)
                else:
                    products_queryset = products_queryset.order_by('name')
            else:
                products_queryset = products_queryset.order_by('name')
            
            # Пагинация
            paginator = Paginator(products_queryset, 12)
            page_number = self.request.GET.get('page')
            products = paginator.get_page(page_number)
            
            context['products'] = products
            context['filter_form'] = filter_form
            context['show_subcategories'] = False
            context['total_products'] = products_queryset.count()
        
        # Хлебные крошки
        breadcrumbs = []
        if category.parent:
            breadcrumbs.append({
                'name': category.parent.name,
                'url': category.parent.get_absolute_url()
            })
        breadcrumbs.append({
            'name': category.name,
            'url': None  # Текущая страница
        })
        context['breadcrumbs'] = breadcrumbs
        
        return context


class ProductDetailView(DetailView):
    """Детальная страница товара"""
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True, is_published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['title'] = product.name
        
        # Увеличиваем счетчик просмотров
        try:
            Product.objects.filter(id=product.id).update(
                views_count=F('views_count') + 1
            )
        except:
            pass
        
        # Получаем похожие товары из той же категории
        try:
            related_products = Product.objects.filter(
                category=product.category,
                is_active=True,
                is_published=True
            ).exclude(id=product.id)[:4]
            context['related_products'] = related_products
        except:
            context['related_products'] = []
        
        return context


class ProductSearchView(ListView):
    """Расширенный поиск товаров"""
    model = Product
    template_name = 'catalog/product_search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        form = ProductSearchForm(self.request.GET)
        queryset = Product.objects.filter(is_active=True, is_published=True)
        
        if form.is_valid():
            # Поиск по тексту
            query = form.cleaned_data.get('q')
            if query:
                queryset = queryset.filter(
                    Q(name__icontains=query) |
                    Q(description__icontains=query) |
                    Q(short_description__icontains=query) |
                    Q(article__icontains=query)
                )
            
            # Фильтр по категории
            category = form.cleaned_data.get('category')
            if category:
                # Включаем товары из подкатегорий
                category_ids = [category.id]
                try:
                    category_ids.extend(
                        category.children.filter(is_active=True).values_list('id', flat=True)
                    )
                except:
                    pass
                queryset = queryset.filter(category_id__in=category_ids)
            
            # Фильтр по подкатегории
            subcategory = form.cleaned_data.get('subcategory')
            if subcategory:
                queryset = queryset.filter(category=subcategory)
            
            # Фильтр по цене
            price_from = form.cleaned_data.get('price_from')
            if price_from:
                queryset = queryset.filter(price__gte=price_from)
            
            price_to = form.cleaned_data.get('price_to')
            if price_to:
                queryset = queryset.filter(price__lte=price_to)
            
            # Фильтр наличия на складе
            in_stock = form.cleaned_data.get('in_stock')
            if in_stock:
                queryset = queryset.filter(stock_quantity__gt=0)
            
            # Фильтр рекомендуемых
            featured = form.cleaned_data.get('featured')
            if featured:
                queryset = queryset.filter(is_featured=True)
            
            # Сортировка
            sort = form.cleaned_data.get('sort')
            if sort:
                queryset = queryset.order_by(sort)
            else:
                queryset = queryset.order_by('name')
        
        return queryset.select_related('category')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск товаров'
        context['search_form'] = ProductSearchForm(self.request.GET)
        context['total_found'] = self.get_queryset().count()
        
        # Статистика поиска
        query = self.request.GET.get('q', '')
        if query:
            context['search_query'] = query
        
        return context


def ajax_subcategories(request):
    """AJAX для получения подкатегорий"""
    category_id = request.GET.get('category_id')
    subcategories = []
    
    if category_id:
        try:
            category = Category.objects.get(id=category_id, is_active=True)
            subcategories = list(
                category.children.filter(is_active=True)
                .values('id', 'name')
                .order_by('name')
            )
        except Category.DoesNotExist:
            pass
    
    return JsonResponse({'subcategories': subcategories})


def ajax_search_suggestions(request):
    """AJAX для автокомплита поиска"""
    query = request.GET.get('q', '').strip()
    suggestions = []
    
    if len(query) >= 2:
        try:
            # Поиск по названиям товаров
            products = Product.objects.filter(
                Q(name__icontains=query) | Q(article__icontains=query),
                is_active=True,
                is_published=True
            )[:10]
            
            suggestions = [
                {
                    'label': product.name,
                    'value': product.name,
                    'url': product.get_absolute_url(),
                    'category': product.category.name,
                    'price': str(product.price)
                }
                for product in products
            ]
        except:
            pass
    
    return JsonResponse({'suggestions': suggestions})


def quick_search_view(request):
    """Быстрый поиск для AJAX запросов"""
    form = QuickSearchForm(request.GET)
    results = []
    
    if form.is_valid() and form.cleaned_data.get('q'):
        query = form.cleaned_data['q']
        try:
            products = Product.objects.filter(
                Q(name__icontains=query) |
                Q(article__icontains=query),
                is_active=True,
                is_published=True
            ).select_related('category')[:5]
            
            results = [
                {
                    'name': product.name,
                    'url': product.get_absolute_url(),
                    'category': product.category.name,
                    'price': str(product.price),
                    'article': product.article
                }
                for product in products
            ]
        except:
            pass
    
    return JsonResponse({'results': results})