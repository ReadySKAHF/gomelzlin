from django.shortcuts import render
from django.views.generic import TemplateView

class DealerListView(TemplateView):
    template_name = 'dealers/dealer_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Дилерские центры'
        context['dealers'] = [
            {
                'name': 'Дилерский центр Минск',
                'city': 'Минск',
                'address': 'пр. Независимости, 125',
                'phone': '+375 17 123-45-67',
                'email': 'minsk@gomelzlin.by'
            },
            {
                'name': 'Дилерский центр Брест',
                'city': 'Брест',
                'address': 'ул. Московская, 45',
                'phone': '+375 162 123-45-67',
                'email': 'brest@gomelzlin.by'
            },
            {
                'name': 'Дилерский центр Витебск',
                'city': 'Витебск',
                'address': 'ул. Ленина, 78',
                'phone': '+375 212 123-45-67',
                'email': 'vitebsk@gomelzlin.by'
            }
        ]
        return context

class DealerDetailView(TemplateView):
    template_name = 'dealers/dealer_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = kwargs.get('pk')
        context['title'] = f'Дилер #{pk}'
        return context