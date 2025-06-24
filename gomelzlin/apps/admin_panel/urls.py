from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    path('products/', views.ProductManagementView.as_view(), name='products'),
    path('orders/', views.OrderManagementView.as_view(), name='orders'),
    path('customers/', views.CustomerManagementView.as_view(), name='customers'),
    path('settings/', views.SettingsView.as_view(), name='settings'),
]