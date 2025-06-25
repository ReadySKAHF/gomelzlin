from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from django.core.paginator import Paginator
from .models import Category, Product


class ProductListView(TemplateView):
    template_name = 'catalog/product_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Каталог товаров'
        
        # Получаем основные категории (без родителей) с количеством товаров
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
                'image': category.image.url if category.image else 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=300&h=200&fit=crop',
                'is_featured': category.is_featured,
                'get_absolute_url': category.get_absolute_url()
            })
        
        context['categories'] = categories_with_counts
        return context
    
    def count_products_in_category(self, category):
        """Подсчитывает количество товаров в категории и всех её подкатегориях"""
        count = category.products.filter(is_active=True, is_published=True).count()
        
        # Добавляем товары из подкатегорий
        for child in category.children.filter(is_active=True):
            count += self.count_products_in_category(child)
        
        return count


class CategoryDetailView(TemplateView):
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
                product_count = subcategory.products.filter(is_active=True, is_published=True).count()
                subcategories_with_counts.append({
                    'id': subcategory.id,
                    'name': subcategory.name,
                    'description': subcategory.description,
                    'slug': subcategory.slug,
                    'product_count': product_count,
                    'image': subcategory.image.url if subcategory.image else 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=300&h=200&fit=crop',
                    'get_absolute_url': subcategory.get_absolute_url()
                })
            
            context['subcategories'] = subcategories_with_counts
            context['show_subcategories'] = True
        else:
            # Показываем товары категории
            products_list = category.products.filter(
                is_active=True, 
                is_published=True
            ).order_by('name')
            
            # Пагинация
            paginator = Paginator(products_list, 12)  # 12 товаров на страницу
            page_number = self.request.GET.get('page')
            products = paginator.get_page(page_number)
            
            context['products'] = products
            context['show_subcategories'] = False
        
        return context


class ProductDetailView(DetailView):
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
        product.increment_views()
        
        # Получаем похожие товары из той же категории
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True,
            is_published=True
        ).exclude(id=product.id)[:4]
        
        context['related_products'] = related_products
        
        return context


class ProductSearchView(ListView):
    model = Product
    template_name = 'catalog/product_search.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        query = self.request.GET.get('q', '')
        category_id = self.request.GET.get('category', '')
        
        queryset = Product.objects.filter(is_active=True, is_published=True)
        
        if query:
            queryset = queryset.filter(
                name__icontains=query
            ) | queryset.filter(
                description__icontains=query
            ) | queryset.filter(
                article__icontains=query
            )
        
        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                # Включаем товары из подкатегорий
                category_ids = [category.id]
                category_ids.extend(
                    category.children.filter(is_active=True).values_list('id', flat=True)
                )
                queryset = queryset.filter(category_id__in=category_ids)
            except Category.DoesNotExist:
                pass
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Поиск товаров'
        context['query'] = self.request.GET.get('q', '')
        context['categories'] = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('name')
        context['selected_category'] = self.request.GET.get('category', '')
        
        return context