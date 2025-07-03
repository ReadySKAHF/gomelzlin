from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Основные страницы каталога
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    
    # Категории и товары
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # AJAX
    path('ajax/quick-search/', views.quick_search_ajax, name='quick_search_ajax'),
    path('ajax/category-search/', views.category_search_ajax, name='category_search_ajax'),
    path('ajax/product-search/', views.product_search_ajax, name='product_search_ajax'),
]