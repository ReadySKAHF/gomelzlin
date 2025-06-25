from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView, DetailView
from .models import Category, Product

class ProductListView(TemplateView):
    template_name = 'catalog/product_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Каталог товаров'
        
        # Получаем категории из базы данных или используем тестовые данные
        try:
            categories = Category.objects.filter(is_active=True, is_featured=True)
            if categories.exists():
                context['categories'] = categories
            else:
                raise Category.DoesNotExist
        except:
            # Тестовые данные, если в базе ничего нет
            context['categories'] = [
                {
                    'name': 'Фитинги',
                    'description': 'Широкий ассортимент фитингов для трубопроводов',
                    'product_count': 156,
                    'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=300&h=200&fit=crop',
                    'slug': 'fittings'
                },
                {
                    'name': 'Трубопроводная арматура',
                    'description': 'Краны, вентили, задвижки и другая запорная арматура',
                    'product_count': 89,
                    'image': 'https://images.unsplash.com/photo-1562577309-2592ab84b1bc?w=300&h=200&fit=crop',
                    'slug': 'valves'
                },
                {
                    'name': 'Литейные изделия',
                    'description': 'Отливки из различных сплавов по индивидуальным заказам',
                    'product_count': 234,
                    'image': 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=300&h=200&fit=crop',
                    'slug': 'castings'
                }
            ]
        
        return context

class CategoryDetailView(TemplateView):
    template_name = 'catalog/category_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        
        try:
            category = Category.objects.get(slug=slug, is_active=True)
            context['category'] = category
            context['title'] = category.name
            context['products'] = Product.objects.filter(category=category, is_active=True, is_published=True)
        except:
            context['title'] = f'Категория: {slug}'
            context['category_name'] = slug.replace('-', ' ').title()
            # Тестовые товары
            context['products'] = [
                {
                    'name': 'Уголок 90° Ду 50',
                    'article': 'УГ-50-90',
                    'price': 25.50,
                    'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=200&h=150&fit=crop',
                    'slug': 'ugolok-90-du-50',
                    'is_in_stock': True
                },
                {
                    'name': 'Тройник Ду 50',
                    'article': 'ТР-50',
                    'price': 32.80,
                    'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=200&h=150&fit=crop',
                    'slug': 'troynik-du-50',
                    'is_in_stock': True
                }
            ]
        
        return context

class ProductDetailView(TemplateView):
    template_name = 'catalog/product_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        
        try:
            product = Product.objects.get(slug=slug, is_active=True, is_published=True)
            context['product'] = product
            context['title'] = product.name
            # Увеличиваем счетчик просмотров
            product.increment_views()
        except:
            context['title'] = f'Товар: {slug}'
            context['product'] = {
                'name': slug.replace('-', ' ').title(),
                'article': 'TEST-001',
                'price': 25.50,
                'description': 'Описание товара будет здесь',
                'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=400&h=400&fit=crop',
                'is_in_stock': True,
                'stock_quantity': 10,
                'weight': 2.5,
                'material': 'Чугун СЧ20',
                'specifications': 'Материал: Чугун СЧ20\nДавление: до 1.6 МПа\nТемпература: до 200°C'
            }
        
        return context