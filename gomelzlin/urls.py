from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('django-admin/', admin.site.urls),
    
    # Main site URLs
    path('', include('apps.core.urls')),
    
    # Authentication
    path('accounts/', include('apps.accounts.urls')),
    
    # Catalog
    path('products/', include('apps.catalog.urls')),
    
    # Orders and Cart
    path('cart/', include('apps.orders.urls')),
    
    # Company information
    path('company/', include('apps.company.urls')),
    
    # Dealers
    path('dealers/', include('apps.dealers.urls')),
    
    # Admin panel
    path('admin-panel/', include('apps.admin_panel.urls')),
]

# Add media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
