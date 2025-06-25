from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ValidationError
import json
from decimal import Decimal

from .models import Cart, CartItem, Order, OrderItem, OrderStatusHistory
from apps.catalog.models import Product


def get_or_create_cart(user=None, session_key=None):
    """Получить или создать корзину для пользователя или сессии"""
    if user and user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=user)
    elif session_key:
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    else:
        return None
    return cart


@method_decorator(login_required, name='dispatch')
class CartView(TemplateView):
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина'
        
        # Получаем корзину пользователя
        cart = get_or_create_cart(user=self.request.user)
        
        if cart:
            context['cart_items'] = cart.items.all().select_related('product')
            context['cart'] = cart
        else:
            context['cart_items'] = []
            context['cart'] = None
        
        return context


@method_decorator(login_required, name='dispatch')
class CheckoutView(TemplateView):
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Оформление заказа'
        
        # Получаем корзину для расчета итоговой суммы
        cart = get_or_create_cart(user=self.request.user)
        if cart and cart.items.exists():
            context['cart'] = cart
            context['cart_items'] = cart.items.all().select_related('product')
        else:
            messages.error(self.request, 'Ваша корзина пуста')
            return redirect('orders:cart')
        
        return context
    
    def post(self, request):
        """Создание заказа"""
        try:
            with transaction.atomic():
                cart = get_or_create_cart(user=request.user)
                
                if not cart or not cart.items.exists():
                    messages.error(request, 'Корзина пуста')
                    return redirect('orders:cart')
                
                # Создаем заказ
                order = Order.objects.create(
                    user=request.user,
                    customer_name=request.POST.get('customer_name', ''),
                    customer_email=request.POST.get('customer_email', request.user.email),
                    customer_phone=request.POST.get('customer_phone', ''),
                    company_name=request.POST.get('company_name', ''),
                    company_unp=request.POST.get('company_unp', ''),
                    company_address=request.POST.get('company_address', ''),
                    delivery_method=request.POST.get('delivery_method', 'pickup'),
                    delivery_address=request.POST.get('delivery_address', ''),
                    payment_method=request.POST.get('payment_method', 'cash'),
                    notes=request.POST.get('notes', ''),
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Переносим товары из корзины в заказ
                total_amount = Decimal('0.00')
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=cart_item.product,
                        quantity=cart_item.quantity,
                        price=cart_item.product.price
                    )
                    total_amount += cart_item.get_total_price()
                
                # Обновляем общую сумму заказа
                order.subtotal = total_amount
                order.total_amount = total_amount
                order.save()
                
                # Очищаем корзину
                cart.clear()
                
                # Создаем запись в истории статусов
                OrderStatusHistory.objects.create(
                    order=order,
                    old_status='',
                    new_status='pending',
                    changed_by=request.user,
                    comment='Заказ создан'
                )
                
                messages.success(request, f'Заказ #{order.number} успешно оформлен!')
                return redirect('orders:order_detail', number=order.number)
        
        except Exception as e:
            messages.error(request, f'Ошибка при оформлении заказа: {str(e)}')
            return redirect('orders:checkout')


class OrderDetailView(TemplateView):
    template_name = 'orders/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        number = kwargs.get('number')
        
        try:
            order = get_object_or_404(Order, number=number)
            
            # Проверяем права доступа
            if order.user != self.request.user and not self.request.user.is_staff:
                messages.error(self.request, 'У вас нет прав для просмотра этого заказа')
                return redirect('core:home')
            
            context['title'] = f'Заказ #{number}'
            context['order'] = order
            context['order_items'] = order.items.all().select_related('product')
            
        except Order.DoesNotExist:
            messages.error(self.request, 'Заказ не найден')
            return redirect('core:home')
        
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
        
        if quantity <= 0:
            return JsonResponse({
                'success': False,
                'message': 'Количество должно быть больше 0'
            })
        
        # Получаем товар
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })
        
        # Получаем или создаем корзину
        cart = get_or_create_cart(
            user=request.user if request.user.is_authenticated else None,
            session_key=request.session.session_key if not request.user.is_authenticated else None
        )
        
        if not cart:
            return JsonResponse({
                'success': False,
                'message': 'Не удалось создать корзину'
            })
        
        # Добавляем товар в корзину
        cart.add_product(product, quantity)
        
        return JsonResponse({
            'success': True,
            'message': f'Товар "{product.name}" добавлен в корзину',
            'cart_count': cart.items_count
        })
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Неверное количество товара'
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
        change = request.POST.get('change')  # 'increase' или 'decrease'
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        # Получаем элемент корзины
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар в корзине не найден'
            })
        
        if change == 'increase':
            cart_item.increase_quantity(1)
        elif change == 'decrease':
            cart_item.decrease_quantity(1)
        elif quantity:
            try:
                new_quantity = int(quantity)
                if new_quantity <= 0:
                    cart_item.delete()
                    return JsonResponse({
                        'success': True,
                        'message': 'Товар удален из корзины',
                        'item_deleted': True
                    })
                else:
                    cart_item.quantity = new_quantity
                    cart_item.save()
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Неверное количество'
                })
        
        # Возвращаем обновленную информацию
        return JsonResponse({
            'success': True,
            'message': 'Корзина обновлена',
            'new_quantity': getattr(cart_item, 'quantity', 0),
            'item_total': float(getattr(cart_item, 'get_total_price', lambda: 0)()),
            'cart_total': float(cart_item.cart.total_price if hasattr(cart_item, 'cart') else 0),
            'cart_count': cart_item.cart.items_count if hasattr(cart_item, 'cart') else 0
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
        
        # Получаем элемент корзины
        try:
            cart_item = CartItem.objects.get(
                id=item_id,
                cart__user=request.user
            )
            cart = cart_item.cart
            product_name = cart_item.product.name
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Товар "{product_name}" удален из корзины',
                'cart_total': float(cart.total_price),
                'cart_count': cart.items_count
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар в корзине не найден'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при удалении товара'
        })


@login_required
@require_POST
def clear_cart_view(request):
    """Очистка корзины"""
    try:
        cart = get_or_create_cart(user=request.user)
        if cart:
            cart.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при очистке корзины'
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


@method_decorator(login_required, name='dispatch')
class OrderListView(TemplateView):
    """Список заказов пользователя"""
    template_name = 'orders/order_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои заказы'
        context['orders'] = Order.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
        return context