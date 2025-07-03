from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django Admin
    path('django-admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),

    # Main site URLs
    path('', include('apps.core.urls')),
    
    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    
    # Catalog
    path('catalog/', include('apps.catalog.urls')),
    
    # Redirect для совместимости
    path('products/', RedirectView.as_view(url='/catalog/', permanent=True)),
    
    # Cart (корзина)
    path('cart/', include(('apps.orders.urls', 'orders'), namespace='cart')),
    
    # Orders (заказы)
    path('orders/', include(('apps.orders.urls', 'orders'), namespace='orders')),
    
    # Company information
    path('company/', include('apps.company.urls')),
    
    # Dealers
    path('dealers/', include('apps.dealers.urls')),
    
    # Admin panel
    path('admin-panel/', include('apps.admin_panel.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'ОАО "ГЗЛиН" - Административная панель'
admin.site.site_title = 'ГЗЛиН Админ'
admin.site.index_title = 'Управление сайтом'