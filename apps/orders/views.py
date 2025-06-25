from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class CartView(TemplateView):
    template_name = 'orders/cart.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Корзина'
        return context

class OrderDetailView(TemplateView):
    template_name = 'orders/order_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        number = kwargs.get('number')
        context['title'] = f'Заказ #{number}'
        context['order_number'] = number
        return context