# apps/admin_panel/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class DashboardView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Админ панель - Дашборд</h1><p>В разработке...</p>')

class ProductManagementView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Управление товарами</h1><p>В разработке...</p>')

class OrderManagementView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Управление заказами</h1><p>В разработке...</p>')

class CustomerManagementView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Управление клиентами</h1><p>В разработке...</p>')

class SettingsView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Настройки</h1><p>В разработке...</p>')