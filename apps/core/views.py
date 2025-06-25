from django.shortcuts import render
from django.views.generic import TemplateView

class HomeView(TemplateView):
    template_name = 'pages/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ОАО "ГЗЛиН" - Главная страница'
        return context

class ContactsView(TemplateView):
    template_name = 'pages/contacts.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Контакты'
        context['company_info'] = {
            'phone': '+375 232 12-34-56',
            'email': 'info@gomelzlin.by',
            'address': '246000, г. Гомель, ул. Промышленная, 15',
            'working_hours': 'Пн-Пт: 8:00-17:00\nСб-Вс: выходной'
        }
        return context