# apps/orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.utils import timezone
import json
from decimal import Decimal
from apps.catalog.models import Product
from .models import Wishlist, WishlistItem

from .models import (
    Cart, CartItem, Order, OrderItem, OrderStatusHistory,
    get_or_create_cart, merge_carts, create_order_from_cart, get_cart_for_request
)
from apps.catalog.models import Product


# Попытаемся импортировать Product, если он существует
try:
    from apps.catalog.models import Product
except ImportError:
    Product = None

from .models import (
    Cart, CartItem, Order, OrderItem, OrderStatusHistory, 
    get_or_create_cart, merge_carts, create_order_from_cart, get_cart_for_request
)
from apps.catalog.models import Product


class CartView(TemplateView):
    """Страница корзины"""
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина'
        
        # Получаем корзину
        cart = get_cart_for_request(self.request)
        
        if cart:
            context['cart_items'] = cart.items.all().select_related('product')
            context['cart'] = cart
        else:
            context['cart_items'] = []
            context['cart'] = None
        
        return context


@require_POST
def add_to_cart(request):
    """AJAX добавление товара в корзину"""
    try:
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        if quantity < 1:
            return JsonResponse({
                'success': False,
                'message': 'Количество должно быть больше 0'
            })
        
        # Получаем товар
        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True,
                is_published=True
            )
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })
        
        # Получаем или создаем корзину
        cart = get_cart_for_request(request)
        
        # Добавляем товар в корзину
        cart_item = cart.add_product(product, quantity)
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} добавлен в корзину',
            'cart_count': cart.items_count,
            'cart_total': str(cart.total_price),
            'item_id': cart_item.id,
            'item_quantity': cart_item.quantity,
            'item_total': str(cart_item.get_total_price())
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


@require_POST
def update_cart_item(request):
    """AJAX обновление количества товара в корзине"""
    try:
        item_id = request.POST.get('item_id')
        change = request.POST.get('change')  # 'increase' или 'decrease'
        
        if not item_id or not change:
            return JsonResponse({
                'success': False,
                'message': 'Неверные параметры'
            })
        
        # Получаем корзину
        cart = get_cart_for_request(request)
        
        # Получаем элемент корзины
        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в корзине'
            })
        
        # Обновляем количество
        if change == 'increase':
            cart_item.increase_quantity()
            
            return JsonResponse({
                'success': True,
                'message': 'Количество увеличено',
                'item_deleted': False,
                'cart_count': cart.items_count,
                'cart_total': str(cart.total_price),
                'item_quantity': cart_item.quantity,
                'item_total': str(cart_item.get_total_price())
            })
            
        elif change == 'decrease':
            updated_item = cart_item.decrease_quantity()
            
            if updated_item is None:
                # Товар был удален
                return JsonResponse({
                    'success': True,
                    'message': 'Товар удален из корзины',
                    'item_deleted': True,
                    'cart_count': cart.items_count,
                    'cart_total': str(cart.total_price)
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Количество уменьшено',
                    'item_deleted': False,
                    'cart_count': cart.items_count,
                    'cart_total': str(cart.total_price),
                    'item_quantity': updated_item.quantity,
                    'item_total': str(updated_item.get_total_price())
                })
        
        return JsonResponse({
            'success': False,
            'message': 'Неверная операция'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при обновлении корзины'
        })

@require_POST
def update_cart_quantity(request):
    """AJAX обновление количества товара прямым вводом"""
    try:
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        if quantity < 0:
            return JsonResponse({
                'success': False,
                'message': 'Количество не может быть отрицательным'
            })
        
        # Получаем корзину
        cart = get_cart_for_request(request)
        
        # Получаем элемент корзины
        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в корзине'
            })
        
        # Обновляем количество
        if quantity == 0:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Товар удален из корзины',
                'item_deleted': True,
                'cart_count': cart.items_count,
                'cart_total': str(cart.total_price)
            })
        else:
            cart_item.quantity = quantity
            cart_item.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Количество обновлено',
                'item_deleted': False,
                'cart_count': cart.items_count,
                'cart_total': str(cart.total_price),
                'item_quantity': cart_item.quantity,
                'item_total': str(cart_item.get_total_price())
            })
        
    except ValueError:
        return JsonResponse({
            'success': False,
            'message': 'Неверное количество'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при обновлении количества'
        })

@require_POST
def remove_from_cart(request):
    """AJAX удаление товара из корзины"""
    try:
        item_id = request.POST.get('item_id')
        
        if not item_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        # Получаем корзину
        cart = get_cart_for_request(request)
        
        # Удаляем элемент корзины
        try:
            cart_item = cart.items.get(id=item_id)
            product_name = cart_item.product.name
            cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'{product_name} удален из корзины',
                'cart_count': cart.items_count,
                'cart_total': str(cart.total_price)
            })
            
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в корзине'
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при удалении товара'
        })

@require_GET
def get_cart_count(request):
    """AJAX получение количества товаров в корзине"""
    try:
        cart = get_cart_for_request(request)
        
        if cart:
            cart_count = cart.items_count
            cart_total = str(cart.total_price)
        else:
            cart_count = 0
            cart_total = '0.00'
        
        return JsonResponse({
            'success': True,
            'cart_count': cart_count,
            'cart_total': cart_total
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'cart_count': 0,
            'cart_total': '0.00',
            'error': str(e)
        })

@require_POST
def clear_cart(request):
    """AJAX очистка корзины"""
    try:
        # Получаем корзину
        cart = get_cart_for_request(request)
        
        # Очищаем корзину
        cart.clear()
        
        return JsonResponse({
            'success': True,
            'message': 'Корзина очищена',
            'cart_count': 0,
            'cart_total': '0.00'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при очистке корзины'
        })

@method_decorator(login_required, name='dispatch')
class CheckoutView(TemplateView):
    """Страница оформления заказа"""
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
            cart = get_or_create_cart(user=request.user)
            
            if not cart or not cart.items.exists():
                messages.error(request, 'Корзина пуста')
                return redirect('orders:cart')
            
            # Получаем IP-адрес клиента
            def get_client_ip():
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                return ip
            
            # Подготавливаем данные заказа с правильными значениями
            order_data = {
                'user': request.user,
                'session_key': request.session.session_key or '',
                
                # Контактная информация
                'customer_name': request.POST.get('customer_name', '').strip(),
                'customer_email': request.POST.get('customer_email', request.user.email).strip(),
                'customer_phone': request.POST.get('customer_phone', '').strip(),
                
                # Информация о компании
                'company_name': request.POST.get('company_name', '').strip(),
                'company_unp': request.POST.get('company_unp', '').strip(),
                'company_address': request.POST.get('company_address', '').strip(),
                
                # Доставка
                'delivery_method': request.POST.get('delivery_method', 'pickup'),
                'delivery_address': request.POST.get('delivery_address', '').strip(),
                'delivery_cost': Decimal('0.00'),  # Будет рассчитано позже
                
                # Оплата
                'payment_method': request.POST.get('payment_method', 'cash'),
                
                # Дополнительная информация
                'notes': request.POST.get('notes', '').strip(),
                
                # Метаинформация
                'ip_address': get_client_ip(),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],  # Ограничиваем длину
            }
            
            # Валидация обязательных полей
            required_fields = ['customer_name', 'customer_email', 'customer_phone']
            for field in required_fields:
                if not order_data.get(field):
                    messages.error(request, f'Поле "{field}" обязательно для заполнения')
                    return redirect('orders:checkout')
            
            # Создаем заказ
            order = create_order_from_cart(cart, order_data)
            
            messages.success(request, f'Заказ №{order.number} успешно создан! Наш менеджер свяжется с вами в ближайшее время.')
            return redirect('orders:order_detail', number=order.number)
                
        except Exception as e:
            print(f"Ошибка создания заказа: {e}")  # Для отладки
            messages.error(request, 'Произошла ошибка при создании заказа. Попробуйте еще раз.')
            return redirect('orders:checkout')

class OrderDetailView(LoginRequiredMixin, TemplateView):
    """Детальная страница заказа"""
    template_name = 'orders/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        order_number = kwargs.get('number')
        order = get_object_or_404(
            Order,
            number=order_number,
            user=self.request.user
        )
        
        context['order'] = order
        context['title'] = f'Заказ №{order.number}'
        context['order_items'] = order.items.all().select_related('product')
        context['status_history'] = order.status_history.all()
        
        return context

class OrderListView(LoginRequiredMixin, TemplateView):
    """Список заказов пользователя"""
    template_name = 'orders/order_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои заказы'
        
        orders = Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')
        
        # Пагинация
        paginator = Paginator(orders, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['orders'] = page_obj
        context['page_obj'] = page_obj
        
        return context


@login_required
@require_POST
def cancel_order(request, order_number):
    """Отмена заказа пользователем"""
    try:
        order = get_object_or_404(
            Order,
            number=order_number,
            user=request.user
        )
        
        if not order.can_be_cancelled:
            messages.error(request, 'Заказ нельзя отменить на текущем этапе')
            return redirect('orders:order_detail', number=order_number)
        
        # Отменяем заказ
        old_status = order.status
        order.status = 'cancelled'  # Используем строковое значение вместо OrderStatus.CANCELLED
        order.save()
        
        # Записываем в историю
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=order.status,
            changed_by=request.user,
            comment='Заказ отменен пользователем'
        )
        
        messages.success(request, f'Заказ №{order.number} отменен')
        return redirect('orders:order_detail', number=order_number)
        
    except Exception as e:
        messages.error(request, 'Произошла ошибка при отмене заказа')
        return redirect('orders:order_list')

# Middleware для объединения корзин при входе в систему
class CartMergeMiddleware:
    """Middleware для объединения корзин при входе пользователя"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Проверяем, если пользователь только что вошел в систему
        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            request.session.get('just_logged_in')):
            
            session_key = request.session.session_key
            if session_key:
                try:
                    # Получаем сессионную корзину
                    session_cart = Cart.objects.get(session_key=session_key)
                    user_cart = get_or_create_cart(user=request.user)
                    
                    # Объединяем корзины
                    merge_carts(session_cart, user_cart)
                    
                except Cart.DoesNotExist:
                    pass
            
            # Удаляем флаг из сессии
            del request.session['just_logged_in']
        
        return response


# Дополнительные вспомогательные представления

def cart_preview_ajax(request):
    """AJAX получение превью корзины для отображения в хедере"""
    try:
        cart = get_cart_for_request(request)
        
        if not cart or not cart.items.exists():
            return JsonResponse({
                'success': True,
                'cart_empty': True,
                'cart_count': 0,
                'cart_total': '0.00',
                'items': []
            })
        
        items_data = []
        for item in cart.items.all()[:5]:  # Показываем только первые 5 товаров
            items_data.append({
                'id': item.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.product.price),
                'total_price': str(item.get_total_price()),
                'product_url': '#'  # Здесь можно добавить URL товара
            })
        
        return JsonResponse({
            'success': True,
            'cart_empty': False,
            'cart_count': cart.items_count,
            'cart_total': str(cart.total_price),
            'items': items_data,
            'has_more': cart.items.count() > 5
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Ошибка получения данных корзины'
        })

@require_POST
def quick_add_to_cart(request):
    """Быстрое добавление товара в корзину с минимальной информацией"""
    try:
        product_id = request.POST.get('product_id')
        
        if not product_id or not Product:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        # Получаем товар
        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True,
                is_published=True
            )
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })
        
        # Получаем корзину
        cart = get_cart_for_request(request)
        
        # Добавляем товар
        cart_item = cart.add_product(product, 1)
        
        return JsonResponse({
            'success': True,
            'message': 'Товар добавлен в корзину',
            'cart_count': cart.items_count
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Ошибка добавления товара'
        })

# Context processor для корзины
def cart_context(request):
    """Контекстный процессор для отображения корзины в шаблонах"""
    cart_count = 0
    
    try:
        if hasattr(request, 'user'):
            cart = get_cart_for_request(request)
            if cart:
                cart_count = cart.items_count
    except Exception:
        cart_count = 0
    
    return {
        'cart_count': cart_count
    }

@login_required
@require_POST
def add_to_wishlist(request):
    """AJAX добавление товара в избранное"""
    try:
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        product = get_object_or_404(Product, id=product_id, is_active=True, is_published=True)
        
        # Получаем или создаем основной список желаний пользователя
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            name='Основной список',
            defaults={'is_public': False}
        )
        
        # Проверяем, есть ли товар уже в списке
        wishlist_item, item_created = WishlistItem.objects.get_or_create(
            wishlist=wishlist,
            product=product
        )
        
        if item_created:
            # Товар добавлен в избранное
            wishlist_count = wishlist.items.count()
            return JsonResponse({
                'success': True,
                'message': f'Товар "{product.name}" добавлен в избранное!',
                'in_wishlist': True,
                'wishlist_count': wishlist_count
            })
        else:
            # Товар уже в избранном
            return JsonResponse({
                'success': False,
                'message': 'Товар уже находится в избранном',
                'in_wishlist': True,
                'wishlist_count': wishlist.items.count()
            })
            
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Товар не найден'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })


@login_required
@require_POST
def remove_from_wishlist(request):
    """AJAX удаление товара из избранного"""
    try:
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        product = get_object_or_404(Product, id=product_id)
        
        # Получаем основной список желаний пользователя
        try:
            wishlist = Wishlist.objects.get(
                user=request.user,
                name='Основной список'
            )
            
            # Удаляем товар из списка
            wishlist_item = WishlistItem.objects.get(
                wishlist=wishlist,
                product=product
            )
            wishlist_item.delete()
            
            wishlist_count = wishlist.items.count()
            
            return JsonResponse({
                'success': True,
                'message': f'Товар "{product.name}" удален из избранного',
                'in_wishlist': False,
                'wishlist_count': wishlist_count
            })
            
        except Wishlist.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Список желаний не найден'
            })
        except WishlistItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в избранном'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Произошла ошибка: {str(e)}'
        })


@login_required
def get_wishlist_status(request):
    """AJAX получение статуса товара в избранном"""
    try:
        product_id = request.GET.get('product_id')
        
        if not product_id:
            return JsonResponse({'in_wishlist': False})
        
        # Проверяем, есть ли товар в избранном
        try:
            wishlist = Wishlist.objects.get(
                user=request.user,
                name='Основной список'
            )
            
            in_wishlist = WishlistItem.objects.filter(
                wishlist=wishlist,
                product_id=product_id
            ).exists()
            
            return JsonResponse({
                'in_wishlist': in_wishlist,
                'wishlist_count': wishlist.items.count()
            })
            
        except Wishlist.DoesNotExist:
            return JsonResponse({
                'in_wishlist': False,
                'wishlist_count': 0
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })


@login_required
def wishlist_count(request):
    """AJAX получение количества товаров в избранном"""
    try:
        wishlist = Wishlist.objects.get(
            user=request.user,
            name='Основной список'
        )
        count = wishlist.items.count()
        
        return JsonResponse({
            'success': True,
            'count': count
        })
        
    except Wishlist.DoesNotExist:
        return JsonResponse({
            'success': True,
            'count': 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка: {str(e)}'
        })