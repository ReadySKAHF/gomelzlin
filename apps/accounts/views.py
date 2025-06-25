from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator

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

@method_decorator(login_required, name='dispatch')
class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Личный кабинет'
        return context

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('core:home')