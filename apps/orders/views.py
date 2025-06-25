from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json


@method_decorator(login_required, name='dispatch')
class CartView(TemplateView):
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина'
        
        # Здесь будет логика получения товаров из корзины
        # Пока используем тестовые данные
        context['cart_items'] = [
            {
                'id': 1,
                'product': {
                    'name': 'Уголок 90° Ду 50',
                    'article': 'УГ-50-90',
                    'price': 25.50,
                    'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=100&h=100&fit=crop'
                },
                'quantity': 2,
                'get_total_price': 51.00
            },
            {
                'id': 2,
                'product': {
                    'name': 'Тройник Ду 50',
                    'article': 'ТР-50',
                    'price': 32.80,
                    'image': 'https://images.unsplash.com/photo-1581092160562-40aa08e78837?w=100&h=100&fit=crop'
                },
                'quantity': 1,
                'get_total_price': 32.80
            }
        ]
        
        context['cart'] = {
            'items_count': 3,
            'total_price': 83.80
        }
        
        return context


@method_decorator(login_required, name='dispatch')
class CheckoutView(TemplateView):
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оформление заказа'
        return context
    
    def post(self, request):
        # Здесь будет логика создания заказа
        # Пока просто перенаправляем с сообщением
        messages.success(request, 'Заказ успешно оформлен! Номер заказа: #20250622-12345')
        return redirect('orders:order_detail', number='20250622-12345')


class OrderDetailView(TemplateView):
    template_name = 'orders/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        number = kwargs.get('number')
        context['title'] = f'Заказ #{number}'
        context['order_number'] = number
        
        # Здесь будет логика получения заказа из базы данных
        # Пока используем тестовые данные
        context['order'] = {
            'number': number,
            'status': 'processing',
            'total_amount': 304.40,
            'created_at': '22.06.2025 14:30',
            'customer_name': 'Иван Иванов',
            'customer_email': 'ivan@example.com',
            'customer_phone': '+375 29 123-45-67',
            'delivery_method': 'pickup',
            'payment_method': 'cash',
            'is_paid': False
        }
        
        return context


@login_required
@require_POST
def add_to_cart_view(request):
    """Добавление товара в корзину"""
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        # Здесь будет логика добавления товара в корзину
        # Пока возвращаем успешный ответ
        
        return JsonResponse({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'cart_count': 3  # Обновленное количество товаров в корзине
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при добавлении товара'
        })


@login_required
@require_POST
def update_cart_view(request):
    """Обновление количества товара в корзине"""
    try:
        item_id = request.POST.get('item_id')
        quantity = request.POST.get('quantity')
        change = request.POST.get('change')
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        # Здесь будет логика обновления корзины
        
        return JsonResponse({
            'success': True,
            'message': 'Корзина обновлена'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при обновлении корзины'
        })


@login_required
@require_POST
def remove_from_cart_view(request):
    """Удаление товара из корзины"""
    try:
        item_id = request.POST.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        # Здесь будет логика удаления товара из корзины
        
        return JsonResponse({
            'success': True,
            'message': 'Товар удален из корзины'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при удалении товара'
        })


# Классы-представления для совместимости с URLs
class AddToCartView(TemplateView):
    def post(self, request):
        return add_to_cart_view(request)


class UpdateCartView(TemplateView):
    def post(self, request):
        return update_cart_view(request)


class RemoveFromCartView(TemplateView):
    def post(self, request):
        return remove_from_cart_view(request)