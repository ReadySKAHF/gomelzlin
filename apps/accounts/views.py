from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from .models import User, UserProfile, CompanyProfile
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
                return redirect('core:home')
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
        # Получаем данные из формы
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        organization = request.POST.get('organization')
        password = request.POST.get('password')
        
        # Проверяем обязательные поля
        if not all([first_name, last_name, email, password]):
            messages.error(request, 'Заполните все обязательные поля')
            return render(request, self.template_name, self.get_context_data())
        
        # Проверяем, не существует ли уже пользователь с таким email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Пользователь с таким email уже существует')
            return render(request, self.template_name, self.get_context_data())
        
        try:
            # Создаем пользователя
            user = User.objects.create_user(
                username=email,  # Используем email как username
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                phone=phone or '',
                user_type='company' if organization else 'individual'
            )
            
            # Создаем профиль пользователя
            profile = UserProfile.objects.create(
                user=user,
                city='',  # Пока оставляем пустым, пользователь заполнит позже
                address='',
            )
            
            # Если указана организация, создаем профиль компании
            if organization:
                company_profile = CompanyProfile.objects.create(
                    user=user,
                    company_name=organization,
                    legal_address='',  # Пользователь заполнит позже
                    unp=''  # Пользователь заполнит позже
                )
            
            # Автоматически входим в систему после регистрации
            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно! Добро пожаловать!')
                return redirect('accounts:profile')  # Перенаправляем в личный кабинет
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
        
        # Получаем или создаем профиль пользователя
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user,
            defaults={
                'city': '',
                'address': '',
                'country': 'Беларусь'
            }
        )
        context['profile'] = profile
        
        # Если пользователь - юридическое лицо, получаем профиль компании
        if self.request.user.is_company:
            try:
                context['company_profile'] = self.request.user.company_profile
            except CompanyProfile.DoesNotExist:
                # Создаем профиль компании, если его нет
                CompanyProfile.objects.create(
                    user=self.request.user,
                    company_name='',
                    legal_address='',
                    unp=''
                )
                context['company_profile'] = self.request.user.company_profile
        
        # Добавляем информацию об избранных товарах
        try:
            wishlist = Wishlist.objects.get(
                user=self.request.user,
                name='Основной список'
            )
            wishlist_items = WishlistItem.objects.filter(
                wishlist=wishlist
            ).select_related('product', 'product__category').order_by('-added_at')
            
            context['wishlist_items'] = wishlist_items
            context['wishlist_count'] = wishlist_items.count()
            
        except Wishlist.DoesNotExist:
            context['wishlist_items'] = []
            context['wishlist_count'] = 0
        
        # Получаем последние заказы пользователя для вкладки "Мои заказы"
        try:
            from apps.orders.models import Order
            recent_orders = Order.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:5]
            context['recent_orders'] = recent_orders
        except:
            context['recent_orders'] = []
        
        return context
    
    def post(self, request):
        form_type = request.POST.get('form_type')
        
        if form_type == 'personal':
            # Обновляем личную информацию
            user = request.user
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.email = request.POST.get('email', '')
            user.phone = request.POST.get('phone', '')
            
            if request.POST.get('birth_date'):
                user.birth_date = request.POST.get('birth_date')
            
            # Обработка загруженного файла аватара
            if request.FILES.get('avatar'):
                user.avatar = request.FILES['avatar']
            
            user.save()
            messages.success(request, 'Личная информация обновлена')
            
        elif form_type == 'settings':
            # Обновляем настройки
            user = request.user
            user.email_notifications = bool(request.POST.get('email_notifications'))
            user.sms_notifications = bool(request.POST.get('sms_notifications'))
            user.save()
            
            # Смена пароля
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if current_password and new_password and confirm_password:
                if user.check_password(current_password):
                    if new_password == confirm_password:
                        if len(new_password) >= 8:
                            user.set_password(new_password)
                            user.save()
                            messages.success(request, 'Пароль успешно изменен')
                            # Повторно аутентифицируем пользователя
                            user = authenticate(request, username=user.email, password=new_password)
                            if user:
                                login(request, user)
                        else:
                            messages.error(request, 'Пароль должен содержать не менее 8 символов')
                    else:
                        messages.error(request, 'Пароли не совпадают')
                else:
                    messages.error(request, 'Неверный текущий пароль')
            
            messages.success(request, 'Настройки обновлены')
            
        elif form_type == 'company' and request.user.is_company:
            # Обновляем реквизиты компании
            try:
                company_profile = request.user.company_profile
                company_profile.company_name = request.POST.get('company_name', '')
                company_profile.unp = request.POST.get('unp', '')
                company_profile.legal_form = request.POST.get('legal_form', 'OOO')
                company_profile.legal_address = request.POST.get('legal_address', '')
                company_profile.bank_account = request.POST.get('bank_account', '')
                company_profile.bank_name = request.POST.get('bank_name', '')
                company_profile.save()
                messages.success(request, 'Реквизиты компании обновлены')
            except CompanyProfile.DoesNotExist:
                messages.error(request, 'Профиль компании не найден')
        
        return redirect('accounts:profile')


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('core:home')