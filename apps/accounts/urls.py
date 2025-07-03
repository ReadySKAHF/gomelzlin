from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Аутентификация
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(next_page='core:home'), name='logout'),
    
    # Профиль
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Управление адресами доставки
    path('address/add/', views.add_delivery_address, name='add_address'),
    path('address/<int:address_id>/update/', views.update_delivery_address, name='update_address'),
    path('address/<int:address_id>/delete/', views.delete_delivery_address, name='delete_address'),
    path('address/<int:address_id>/set-default/', views.set_default_address, name='set_default_address'),
]