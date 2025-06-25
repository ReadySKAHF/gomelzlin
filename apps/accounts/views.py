# apps/accounts/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class LoginView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Страница входа</h1><p>В разработке...</p>')

class RegisterView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Страница регистрации</h1><p>В разработке...</p>')

class LogoutView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Выход из системы</h1><p>В разработке...</p>')

class ProfileView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Профиль пользователя</h1><p>В разработке...</p>')

# apps/catalog/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class ProductListView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Каталог товаров</h1><p>В разработке...</p>')

class CategoryDetailView(TemplateView):
    def get(self, request, slug):
        return HttpResponse(f'<h1>Категория: {slug}</h1><p>В разработке...</p>')

class ProductDetailView(TemplateView):
    def get(self, request, slug):
        return HttpResponse(f'<h1>Товар: {slug}</h1><p>В разработке...</p>')