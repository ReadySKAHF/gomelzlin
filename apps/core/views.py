from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse

class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ОАО "ГЗЛиН" - Главная страница'
        return context

class ContactsView(TemplateView):
    template_name = 'company/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        return context

# Простые обработчики ошибок (добавим позже)
def custom_404(request, exception):
    return HttpResponse('<h1>Страница не найдена</h1><p>404 Error</p>', status=404)

def custom_500(request):
    return HttpResponse('<h1>Внутренняя ошибка сервера</h1><p>500 Error</p>', status=500)

def custom_403(request, exception):
    return HttpResponse('<h1>Доступ запрещен</h1><p>403 Error</p>', status=403)