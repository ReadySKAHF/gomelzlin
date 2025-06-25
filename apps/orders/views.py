# apps/orders/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class CartView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Корзина</h1><p>В разработке...</p>')

class AddToCartView(TemplateView):
    def post(self, request):
        return HttpResponse('<h1>Добавление в корзину</h1><p>В разработке...</p>')

class UpdateCartView(TemplateView):
    def post(self, request):
        return HttpResponse('<h1>Обновление корзины</h1><p>В разработке...</p>')

class RemoveFromCartView(TemplateView):
    def post(self, request):
        return HttpResponse('<h1>Удаление из корзины</h1><p>В разработке...</p>')

class CheckoutView(TemplateView):
    def get(self, request):
        return HttpResponse('<h1>Оформление заказа</h1><p>В разработке...</p>')

class OrderDetailView(TemplateView):
    def get(self, request, number):
        return HttpResponse(f'<h1>Заказ: {number}</h1><p>В разработке...</p>')