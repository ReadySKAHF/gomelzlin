from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
import json

from .models import User, UserProfile, CompanyProfile, DeliveryAddress
from apps.orders.models import Wishlist, WishlistItem

class LoginView(TemplateView):
    template_name = 'accounts/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход в систему'
        return context
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Добро пожаловать!')
                return redirect('accounts:profile')
            else:
                messages.error(request, 'Неверный email или пароль')
        else:
            messages.error(request, 'Заполните все поля')
        
        return render(request, self.template_name, self.get_context_data())


class RegisterView(TemplateView):
    template_name = 'accounts/register.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context
    
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization')
        password = request.POST.get('password')
        
        if not all([first_name, last_name, email, password]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, self.template_name, self.get_context_data())
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, self.template_name, self.get_context_data())
        
        try:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone or '',
                user_type='company' if organization else 'individual'
            )
            
            profile = UserProfile.objects.create(
                user=user,
                city='',
                address='',
            )
            
            if organization:
                company_profile = CompanyProfile.objects.create(
                    user=user,
                    company_name=organization,
                    legal_address='', 
                    unp=''  
                )
            
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
                return redirect('accounts:profile')  
            else:
                messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти в систему.')
                return redirect('accounts:login')
                
        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {str(e)}')
            return render(request, self.template_name, self.get_context_data())


@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Личный кабинет'
        
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'city': '',
                'address': '',
                'country': 'Беларусь'
            }
        )
        context['profile'] = profile
        
        if self.request.user.is_company:
            try:
                context['company_profile'] = self.request.user.company_profile
            except CompanyProfile.DoesNotExist:
                CompanyProfile.objects.create(
                    user=self.request.user,
                    company_name='',
                    legal_address='',
                    unp=''
                )
                context['company_profile'] = self.request.user.company_profile
        
        context['delivery_addresses'] = DeliveryAddress.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-is_default', '-created_at')
        
        try:
            wishlist = Wishlist.objects.get(user=self.request.user)
            context['wishlist_items'] = WishlistItem.objects.filter(
                wishlist=wishlist
            ).select_related('product').order_by('-added_at')[:6] 
            context['wishlist_count'] = WishlistItem.objects.filter(wishlist=wishlist).count()
        except Wishlist.DoesNotExist:
            context['wishlist_items'] = []
            context['wishlist_count'] = 0
        
        try:

            try:
                from apps.orders.models import Order
                print("DEBUG: Order model imported successfully")
            except ImportError as e:
                print(f"DEBUG: Cannot import Order model: {e}")
                context['recent_orders'] = []
                context['orders_count'] = 0
                return context
            
            total_orders = Order.objects.filter(user=self.request.user).count()
            print(f"DEBUG: Total orders for user: {total_orders}")
            
            recent_orders = Order.objects.filter(
                user=self.request.user
            ).prefetch_related('items__product').order_by('-created_at')[:10]
            
            context['recent_orders'] = recent_orders
            context['orders_count'] = total_orders
            
        except Exception as e:
            print(f"DEBUG: Error loading orders: {e}")
            print(f"DEBUG: Error type: {type(e)}")
            import traceback
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            
            context['recent_orders'] = []
            context['orders_count'] = 0
        
        return context

@login_required
@require_POST
def add_delivery_address(request):
    """AJAX добавление адреса доставки"""
    try:
        title = request.POST.get('title', '').strip()
        city = request.POST.get('city', '').strip()
        address = request.POST.get('address', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        contact_person = request.POST.get('contact_person', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()
        notes = request.POST.get('notes', '').strip()
        is_default = request.POST.get('is_default') == 'on'
        
        if not all([title, city, address]):
            return JsonResponse({
                'success': False,
                'message': 'Заполните обязательные поля: название, город, адрес'
            })
        
        delivery_address = DeliveryAddress.objects.create(
            user=request.user,
            title=title,
            city=city,
            address=address,
            postal_code=postal_code,
            contact_person=contact_person,
            contact_phone=contact_phone,
            notes=notes,
            is_default=is_default
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Адрес доставки добавлен',
            'address': {
                'id': delivery_address.id,
                'title': delivery_address.title,
                'full_address': delivery_address.get_full_address(),
                'is_default': delivery_address.is_default
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при добавлении адреса: {str(e)}'
        })


@login_required
@require_POST
def update_delivery_address(request, address_id):
    """AJAX обновление адреса доставки"""
    try:
        address = get_object_or_404(
            DeliveryAddress, 
            id=address_id, 
            user=request.user
        )
        
        address.title = request.POST.get('title', address.title).strip()
        address.city = request.POST.get('city', address.city).strip()
        address.address = request.POST.get('address', address.address).strip()
        address.postal_code = request.POST.get('postal_code', address.postal_code).strip()
        address.contact_person = request.POST.get('contact_person', address.contact_person).strip()
        address.contact_phone = request.POST.get('contact_phone', address.contact_phone).strip()
        address.notes = request.POST.get('notes', address.notes).strip()
        address.is_default = request.POST.get('is_default') == 'on'
        
        address.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Адрес обновлен',
            'address': {
                'id': address.id,
                'title': address.title,
                'full_address': address.get_full_address(),
                'is_default': address.is_default
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при обновлении адреса: {str(e)}'
        })


@login_required
@require_POST
def delete_delivery_address(request, address_id):
    """AJAX удаление адреса доставки"""
    try:
        address = get_object_or_404(
            DeliveryAddress, 
            id=address_id, 
            user=request.user
        )
        
        address.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Адрес удален'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при удалении адреса: {str(e)}'
        })


@login_required
@require_POST
def set_default_address(request, address_id):
    """AJAX установка адреса по умолчанию"""
    try:
        address = get_object_or_404(
            DeliveryAddress, 
            id=address_id, 
            user=request.user
        )
        
        DeliveryAddress.objects.filter(user=request.user).update(is_default=False)
        
        address.is_default = True
        address.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Адрес установлен по умолчанию'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при установке адреса по умолчанию: {str(e)}'
        })

@login_required
@require_GET
def get_delivery_address_info(request, address_id):
    """API для получения полной информации об адресе доставки"""
    try:
        address = get_object_or_404(
            DeliveryAddress,
            id=address_id,
            user=request.user,
            is_active=True
        )
        
        return JsonResponse({
            'success': True,
            'address': {
                'id': address.id,
                'title': address.title,
                'country': address.country,
                'city': address.city,
                'address': address.address,
                'postal_code': address.postal_code,
                'contact_person': address.contact_person,
                'contact_phone': address.contact_phone,
                'notes': address.notes,
                'is_default': address.is_default,
                'full_address': address.get_full_address(),
                'short_address': address.get_short_address(),
                'created_at': address.created_at.strftime('%d.%m.%Y')
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Ошибка при получении информации об адресе: {str(e)}'
        })