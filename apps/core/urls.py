from django.urls import path
from . import views
from django.views.generic import TemplateView
from apps.company.views import AboutView

app_name = 'core'

urlpatterns = [
    # Главная страница
    path('', views.HomeView.as_view(), name='home'),
    
    # Новости
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='news_detail'),
    
    # О компании
    path('about/', AboutView.as_view(), name='about'),
    
    # Дилерские центры
    path('dealers/', TemplateView.as_view(template_name='pages/dealers.html'), name='dealers'),
    
    # Контакты
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    
    # Дополнительные страницы
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('delivery/', TemplateView.as_view(template_name='pages/delivery.html'), name='delivery'),
    path('warranty/', TemplateView.as_view(template_name='pages/warranty.html'), name='warranty'),
]