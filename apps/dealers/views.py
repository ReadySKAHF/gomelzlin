from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.http import JsonResponse
from .models import DealerCenter

class DealerListView(ListView):
    """Список дилерских центров"""
    model = DealerCenter
    template_name = 'pages/dealers.html'
    context_object_name = 'dealers'
    
    def get_queryset(self):
        """Получаем только активных дилеров"""
        return DealerCenter.objects.active().select_related()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dealers = self.get_queryset()
        dealers_by_region = {}
        
        for dealer in dealers:
            region = dealer.region
            if region not in dealers_by_region:
                dealers_by_region[region] = []
            dealers_by_region[region].append(dealer)
        
        context.update({
            'title': 'Дилерские центры',
            'dealers_by_region': dealers_by_region,
            'total_dealers': dealers.count(),
            'featured_dealers': dealers.filter(is_featured=True),
        })
        
        return context

class DealerDetailView(DetailView):
    """Детальная страница дилерского центра"""
    model = DealerCenter
    template_name = 'dealers/dealer_detail.html'
    context_object_name = 'dealer'
    
    def get_queryset(self):
        """Только активные дилеры"""
        return DealerCenter.objects.active()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dealer = self.object
        
        context.update({
            'title': f'{dealer.name} - {dealer.city}',
            'meta_description': f'Дилерский центр {dealer.name} в городе {dealer.city}. '
                              f'Контакты: {dealer.phone}, {dealer.email}',
        })
        
        return context


def dealer_map_data(request):
    """API для получения данных дилеров для карты"""
    dealers = DealerCenter.objects.active().filter(
        latitude__isnull=False,
        longitude__isnull=False
    )
    
    map_data = []
    for dealer in dealers:
        map_data.append({
            'id': dealer.id,
            'name': dealer.name,
            'city': dealer.city,
            'address': dealer.address,
            'phone': dealer.phone,
            'email': dealer.email,
            'latitude': float(dealer.latitude),
            'longitude': float(dealer.longitude),
            'yandex_url': dealer.yandex_maps_url,
            'dealer_type': dealer.dealer_type_display,
            'working_hours': dealer.working_hours,
        })
    
    return JsonResponse({
        'dealers': map_data,
        'total': len(map_data)
    })


def dealer_regions(request):
    """API для получения списка регионов с количеством дилеров"""
    from django.db.models import Count
    
    regions = DealerCenter.objects.active().values(
        'region'
    ).annotate(
        count=Count('id')
    ).order_by('region')
    
    region_data = []
    for region in regions:
        region_code = region['region']
        region_name = dict(DealerCenter.REGIONS).get(region_code, region_code)
        region_data.append({
            'code': region_code,
            'name': region_name,
            'count': region['count']
        })
    
    return JsonResponse({
        'regions': region_data,
        'total_regions': len(region_data)
    })