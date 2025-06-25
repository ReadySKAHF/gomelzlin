# apps/catalog/urls.py
from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    # Основные страницы
    path('', views.ProductListView.as_view(), name='product_list'),
    path('search/', views.ProductSearchView.as_view(), name='product_search'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # AJAX endpoints
    path('ajax/subcategories/', views.ajax_subcategories, name='ajax_subcategories'),
    path('ajax/search-suggestions/', views.ajax_search_suggestions, name='ajax_search_suggestions'),
    path('ajax/quick-search/', views.quick_search_view, name='ajax_quick_search'),
]