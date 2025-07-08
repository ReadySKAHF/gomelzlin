from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from .models import DealerCenter
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.db import models

class DealerListView(ListView):
    """Список дилерских центров"""
    model = DealerCenter
    template_name = 'pages/dealers.html'
    context_object_name = 'dealers'
    
    def get_queryset(self):
        """Получаем только активных дилеров, сортированных по типу и порядку"""
        return DealerCenter.objects.filter(is_active=True).order_by(
            models.Case(
                models.When(dealer_type='factory', then=0), 
                default=1
            ),
            'sort_order', 
            'name'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dealers = self.get_queryset()

        dealers_by_region = {}
        factories = []
        regular_dealers = []
        
        for dealer in dealers:
            if dealer.dealer_type == 'factory':
                factories.append(dealer)
            else:
                regular_dealers.append(dealer)
                region = dealer.region
                if region not in dealers_by_region:
                    dealers_by_region[region] = []
                dealers_by_region[region].append(dealer)

        dealers_data = []
        for dealer in dealers:
            if dealer.has_coordinates: 
                dealers_data.append({
                    'id': dealer.id,
                    'name': dealer.name,
                    'address': dealer.full_address,
                    'coords': [float(dealer.latitude), float(dealer.longitude)],
                    'type': dealer.dealer_type,
                    'description': dealer.description or f'{dealer.dealer_type_display} в {dealer.city}',
                    'phone': dealer.phone,
                    'email': dealer.email,
                    'city': dealer.city,
                    'working_hours': dealer.working_hours,
                    'is_featured': dealer.is_featured,
                    'website': dealer.website or '',
                    'is_factory': dealer.dealer_type == 'factory',
                })
        
        context.update({
            'title': 'Дилерские центры',
            'dealers_by_region': dealers_by_region,
            'factories': factories,
            'regular_dealers': regular_dealers,
            'total_dealers': dealers.count(),
            'featured_dealers': dealers.filter(is_featured=True),
            'dealers_json': json.dumps(dealers_data, cls=DjangoJSONEncoder, ensure_ascii=False),
            'has_dealers_with_coords': any(d['coords'] for d in dealers_data),
        })
        
        return context

class DealerDetailView(DetailView):
    """Детальная страница дилерского центра"""
    model = DealerCenter
    template_name = 'dealers/dealer_detail.html'
    context_object_name = 'dealer'
    
    def get_queryset(self):
        """Только активные дилеры"""
        return DealerCenter.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dealer = self.object
        
        context.update({
            'title': f'{dealer.name} - {dealer.city}',
            'meta_description': f'Дилерский центр {dealer.name} в городе {dealer.city}. '
                              f'Адрес: {dealer.full_address}. '
                              f'Телефон: {dealer.phone}',
        })
        
        return context

def dealer_map_data(request):
    """API endpoint для получения данных карты дилеров"""
    dealers = DealerCenter.objects.filter(is_active=True).order_by(
        models.Case(
            models.When(dealer_type='factory', then=0),
            default=1
        ),
        'sort_order', 
        'name'
    )
    
    dealers_data = []

    for dealer in dealers:
        if dealer.has_coordinates: 
            dealers_data.append({
                'id': dealer.id,
                'name': dealer.name,
                'address': dealer.full_address,
                'coords': [float(dealer.latitude), float(dealer.longitude)],
                'type': dealer.dealer_type,
                'description': dealer.description or f'{dealer.dealer_type_display} в {dealer.city}',
                'phone': dealer.phone,
                'email': dealer.email,
                'city': dealer.city,
                'working_hours': dealer.working_hours,
                'is_featured': dealer.is_featured,
                'website': dealer.website or '',
                'is_factory': dealer.dealer_type == 'factory',
            })
    
    return JsonResponse({
        'dealers': dealers_data,
        'total': len(dealers_data),
        'success': True
    })

def dealer_regions(request):
    """API endpoint для получения дилеров по регионам"""
    dealers = DealerCenter.objects.filter(is_active=True).order_by('sort_order', 'name')
    
    regions_data = {}
    factories_data = []
    
    for dealer in dealers:
        if dealer.dealer_type == 'factory':
            factories_data.append({
                'id': dealer.id,
                'name': dealer.name,
                'city': dealer.city,
                'address': dealer.address,
                'phone': dealer.phone,
                'email': dealer.email,
                'dealer_type': dealer.get_dealer_type_display(),
                'is_featured': dealer.is_featured,
            })
        else:
            region = dealer.get_region_display()
            if region not in regions_data:
                regions_data[region] = []
            
            regions_data[region].append({
                'id': dealer.id,
                'name': dealer.name,
                'city': dealer.city,
                'address': dealer.address,
                'phone': dealer.phone,
                'email': dealer.email,
                'dealer_type': dealer.get_dealer_type_display(),
                'is_featured': dealer.is_featured,
            })
    
    return JsonResponse({
        'regions': regions_data,
        'factories': factories_data,
        'success': True
    })