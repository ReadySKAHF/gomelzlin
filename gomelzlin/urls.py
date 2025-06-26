from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    # Django Admin
    path('django-admin/', admin.site.urls),
    
    # Main site URLs
    path('', include('apps.core.urls')),
    
    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    
    # Catalog
    path('catalog/', include('apps.catalog.urls')),
    path('products/', RedirectView.as_view(url='/catalog/', permanent=True)),
    # path('products/', include('apps.catalog.urls')),
    
    # Orders and Cart
    path('cart/', include('apps.orders.urls')),
    
    # Orders and Cart
    path('', include('apps.orders.urls')),
    
    # Company information
    path('company/', include('apps.company.urls')),
    
    # Dealers
    path('dealers/', include('apps.dealers.urls')),
    
    # Admin panel
    path('admin-panel/', include('apps.admin_panel.urls')),

    path('catalog/', include('apps.catalog.urls')),
]

# Add media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Настройка заголовков админки
admin.site.site_header = 'ОАО "ГЗЛиН" - Административная панель'
admin.site.site_title = 'ГЗЛиН Админ'
admin.site.index_title = 'Управление сайтом'