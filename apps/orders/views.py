from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q  
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.utils import timezone
import json
import logging
from decimal import Decimal

from apps.accounts.models import UserProfile, CompanyProfile, DeliveryAddress

from apps.catalog.models import Product
from .models import (
    Cart, CartItem, Order, OrderItem, OrderStatusHistory, Wishlist, WishlistItem,
    get_or_create_cart, merge_carts, create_order_from_cart, get_cart_for_request
)

logger = logging.getLogger(__name__)

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
        
        logger.info(f"Add to cart request: product_id={product_id}, quantity={quantity}, user={request.user}")
        
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
        
        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True,
                is_published=True
            )
        except Product.DoesNotExist:
            logger.error(f"Product not found: id={product_id}")
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден или недоступен'
            })
        
        cart = get_cart_for_request(request)
        
        if not cart:
            logger.error("Failed to create cart")
            return JsonResponse({
                'success': False,
                'message': 'Не удалось создать корзину'
            })
        
        try:
            cart_item = cart.add_product(product, quantity)
            
            return JsonResponse({
                'success': True,
                'message': f'Товар "{product.name}" добавлен в корзину',
                'cart_count': cart.items_count,
                'cart_total': str(cart.total_price),
                'item_id': cart_item.id,
                'item_quantity': cart_item.quantity,
                'item_total': str(cart_item.get_total_price())
            })
            
        except Exception as e:
            logger.error(f"Error adding product to cart: {e}")
            return JsonResponse({
                'success': False,
                'message': 'Ошибка при добавлении товара в корзину'
            })
        
    except ValueError as e:
        logger.error(f"ValueError in add_to_cart: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Неверное количество товара'
        })
    except Exception as e:
        logger.error(f"Unexpected error in add_to_cart: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла неожиданная ошибка'
        })


@require_POST
def update_cart_item(request):
    """AJAX обновление количества товара в корзине"""

    try:
        item_id = request.POST.get('item_id')
        change = request.POST.get('change') 
        
        if not item_id or not change:
            return JsonResponse({
                'success': False,
                'message': 'Неверные параметры'
            })
        
        cart = get_cart_for_request(request)
        
        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в корзине'
            })
        
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
        
        cart = get_cart_for_request(request)
        
        try:
            cart_item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден в корзине'
            })
        
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
        
        cart = get_cart_for_request(request)
        
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
        cart = get_cart_for_request(request)
        
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

        cart = get_or_create_cart(user=self.request.user)
        if cart and cart.items.exists():
            context['cart'] = cart
            context['cart_items'] = cart.items.all().select_related('product')
        else:
            messages.error(self.request, 'Ваша корзина пуста')
            return redirect('cart:cart')

        try:
            profile = self.request.user.profile
            context['profile'] = profile
        except UserProfile.DoesNotExist:
            context['profile'] = None

        if self.request.user.is_company:
            try:
                context['company_profile'] = self.request.user.company_profile
            except CompanyProfile.DoesNotExist:
                context['company_profile'] = None

        context['delivery_addresses'] = DeliveryAddress.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-is_default', '-created_at')

        default_address = DeliveryAddress.objects.filter(
            user=self.request.user,
            is_default=True,
            is_active=True
        ).first()
        context['default_address'] = default_address
        
        return context
    
    def post(self, request):
        """Создание заказа"""
        try:
            cart = get_or_create_cart(user=request.user)
            
            if not cart or not cart.items.exists():
                messages.error(request, 'Корзина пуста')
                return redirect('cart:cart')

            def get_client_ip():
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')
                return ip

            delivery_address_text = ''
            delivery_method = request.POST.get('delivery_method', 'pickup')
            
            if delivery_method != 'pickup':
                saved_address_id = request.POST.get('saved_address_id')
                if saved_address_id and saved_address_id != 'new':
                    try:
                        saved_address = DeliveryAddress.objects.get(
                            id=saved_address_id,
                            user=request.user,
                            is_active=True
                        )
                        delivery_address_text = saved_address.get_full_address()
                        if saved_address.contact_person:
                            delivery_address_text += f"\nКонтактное лицо: {saved_address.contact_person}"
                        if saved_address.contact_phone:
                            delivery_address_text += f"\nТелефон: {saved_address.contact_phone}"
                        if saved_address.notes:
                            delivery_address_text += f"\nПримечания: {saved_address.notes}"
                    except DeliveryAddress.DoesNotExist:
                        messages.error(request, 'Выбранный адрес не найден')
                        return redirect('orders:checkout')
                else:
                    delivery_address_text = request.POST.get('delivery_address', '').strip()
                    if not delivery_address_text:
                        messages.error(request, 'Укажите адрес доставки')
                        return redirect('orders:checkout')
            
            order_data = {
                'user': request.user,
                'session_key': request.session.session_key or '',
                
                'customer_name': request.POST.get('customer_name', '').strip() or request.user.get_full_name(),
                'customer_email': request.POST.get('customer_email', request.user.email).strip(),
                'customer_phone': request.POST.get('customer_phone', '').strip() or request.user.phone,
                
                'company_name': request.POST.get('company_name', '').strip(),
                'company_unp': request.POST.get('company_unp', '').strip(),
                'company_address': request.POST.get('company_address', '').strip(),
                
                'delivery_method': delivery_method,
                'delivery_address': delivery_address_text,
                'delivery_cost': Decimal('0.00'), 
                
                'payment_method': request.POST.get('payment_method', 'cash'),
                
                'notes': request.POST.get('notes', '').strip(),
                
                'ip_address': get_client_ip(),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],  
            }
            
            if request.user.is_company:
                try:
                    company_profile = request.user.company_profile
                    if not order_data['company_name'] and company_profile.company_name:
                        order_data['company_name'] = company_profile.company_name
                    if not order_data['company_unp'] and company_profile.unp:
                        order_data['company_unp'] = company_profile.unp
                    if not order_data['company_address'] and company_profile.legal_address:
                        order_data['company_address'] = company_profile.legal_address
                except:
                    pass  
            
            required_fields = ['customer_name', 'customer_email', 'customer_phone']
            for field in required_fields:
                if not order_data.get(field):
                    field_names = {
                        'customer_name': 'Имя',
                        'customer_email': 'Email',
                        'customer_phone': 'Телефон'
                    }
                    messages.error(request, f'Поле "{field_names[field]}" обязательно для заполнения')
                    return redirect('orders:checkout')

            order = create_order_from_cart(cart, order_data)
            
            messages.success(request, f'Заказ №{order.number} успешно создан! Наш менеджер свяжется с вами в ближайшее время.')
            return redirect('orders:order_detail', number=order.number)
                
        except Exception as e:
            print(f"Ошибка создания заказа: {e}") 
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
    """Список заказов пользователя с поиском и пагинацией"""
    template_name = 'orders/order_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Мои заказы'
        
        search_query = self.request.GET.get('search', '').strip()
        status_filter = self.request.GET.get('status', '')
        
        orders = Order.objects.filter(
            user=self.request.user
        ).prefetch_related('items').order_by('-created_at')
        
        if search_query:
            from django.db.models import Q
            orders = orders.filter(
                Q(number__icontains=search_query) |
                Q(customer_name__icontains=search_query) |
                Q(customer_email__icontains=search_query) |
                Q(customer_phone__icontains=search_query)
            )
        
        if status_filter:
            orders = orders.filter(status=status_filter)
        
        from django.core.paginator import Paginator
        paginator = Paginator(orders, 4) 
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context['orders'] = page_obj
        context['page_obj'] = page_obj
        context['search_query'] = search_query
        context['status_filter'] = status_filter
        
        context['status_choices'] = Order.STATUS_CHOICES
        
        context['total_orders_count'] = Order.objects.filter(user=self.request.user).count()
        
        return context

@login_required
@require_POST
def cancel_order(request, number):
    """Отмена заказа пользователем с поддержкой AJAX"""
    try:
        order = get_object_or_404(
            Order,
            number=number,
            user=request.user
        )
        
        if not order.can_be_cancelled:
            error_message = 'Заказ нельзя отменить на текущем этапе'

            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'message': error_message
                })
            else:
                messages.error(request, error_message)
                return redirect('orders:order_detail', number=number)
        
        old_status = order.status
        order.status = 'cancelled'
        order.save()

        try:
            from .models import OrderStatusHistory
            OrderStatusHistory.objects.create(
                order=order,
                old_status=old_status,
                new_status='cancelled',
                comment='Заказ отменен пользователем'
            )
        except:
            pass  
        
        success_message = f'Заказ №{order.number} успешно отменен'

        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True,
                'message': success_message,
                'order_status': 'cancelled'
            })
        else:
            messages.success(request, success_message)
            return redirect('accounts:profile')
        
    except Exception as e:
        error_message = 'Произошла ошибка при отмене заказа'
        print(f"Ошибка отмены заказа: {e}")

        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': False,
                'message': error_message
            })
        else:
            messages.error(request, error_message)
            return redirect('accounts:profile')

class CartMergeMiddleware:
    """Middleware для объединения корзин при входе пользователя"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)

        if (hasattr(request, 'user') and 
            request.user.is_authenticated and 
            request.session.get('just_logged_in')):
            
            session_key = request.session.session_key
            if session_key:
                try:
                    session_cart = Cart.objects.get(session_key=session_key)
                    user_cart = get_or_create_cart(user=request.user)
                    
                    merge_carts(session_cart, user_cart)
                    
                except Cart.DoesNotExist:
                    pass

            del request.session['just_logged_in']
        
        return response

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
        for item in cart.items.all()[:5]:  
            items_data.append({
                'id': item.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'unit_price': str(item.product.price),
                'total_price': str(item.get_total_price()),
                'product_url': '#' 
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
        
        cart = get_cart_for_request(request)
        
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
    """AJAX добавление/удаление товара в избранное"""
    try:
        product_id = request.POST.get('product_id')
        
        if not product_id:
            return JsonResponse({
                'success': False,
                'message': 'Не указан товар'
            })
        
        product = get_object_or_404(Product, id=product_id, is_active=True, is_published=True)
        
        wishlist, created = Wishlist.objects.get_or_create(
            user=request.user,
            name='Основной список',
            defaults={'is_public': False}
        )
        
        try:
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
            
        except WishlistItem.DoesNotExist:
            WishlistItem.objects.create(
                wishlist=wishlist,
                product=product
            )
            wishlist_count = wishlist.items.count()
            
            return JsonResponse({
                'success': True,
                'message': f'Товар "{product.name}" добавлен в избранное!',
                'in_wishlist': True,
                'wishlist_count': wishlist_count
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

        try:
            wishlist = Wishlist.objects.get(
                user=request.user,
                name='Основной список'
            )

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

@login_required
@require_POST
def reorder_items(request, number):
    """Повторный заказ - добавление товаров из заказа в корзину"""
    try:
        order = get_object_or_404(
            Order,
            number=number,
            user=request.user
        )

        cart = get_cart_for_request(request)
        
        added_items = 0
        unavailable_items = []

        for order_item in order.items.all():
            try:
                product = order_item.product

                if not product.is_active:
                    unavailable_items.append(product.name)
                    continue

                cart_item, created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': order_item.quantity}
                )
                
                if not created:
                    cart_item.quantity += order_item.quantity
                    cart_item.save()
                
                added_items += 1
                
            except Exception as e:
                print(f"Ошибка при добавлении товара {order_item.product.name}: {e}")
                unavailable_items.append(order_item.product.name)
                continue

        if added_items > 0:
            cart_count = cart.items_count if hasattr(cart, 'items_count') else cart.items.count()
            
            message = f"Добавлено {added_items} товар"
            if added_items == 1:
                message += " в корзину"
            elif added_items in [2, 3, 4]:
                message += "а в корзину"
            else:
                message += "ов в корзину"
            
            if unavailable_items:
                message += f". Недоступно: {len(unavailable_items)} товар"
                if len(unavailable_items) in [2, 3, 4]:
                    message += "а"
                elif len(unavailable_items) > 4:
                    message += "ов"
            
            return JsonResponse({
                'success': True,
                'message': message,
                'added_items': added_items,
                'unavailable_items': len(unavailable_items),
                'cart_count': cart_count
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Ни один товар из заказа не удалось добавить в корзину. Возможно, все товары недоступны.'
            })
            
    except Order.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Заказ не найден'
        })
        
    except Exception as e:
        print(f"Ошибка при повторном заказе: {e}")
        return JsonResponse({
            'success': False,
            'message': 'Произошла ошибка при добавлении товаров в корзину'
        })