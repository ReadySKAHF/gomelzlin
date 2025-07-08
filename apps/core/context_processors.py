from django.conf import settings

def api_keys(request):
    """
    Контекст процессор для передачи API ключей в шаблоны
    """
    return {
        'YANDEX_MAPS_API_KEY': getattr(settings, 'YANDEX_MAPS_API_KEY', ''),
    }