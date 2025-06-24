from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from apps.core.sitemaps import StaticViewSitemap, ProductSitemap, CategorySitemap

# Sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
    'categories': CategorySitemap,
}

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
    
    # Customers
    path('customers/', include('apps.customers.urls')),
    
    # Company information
    path('', include('apps.company.urls')),
    
    # Dealers
    path('dealers/', include('apps.dealers.urls')),
    
    # Admin panel
    path('admin-panel/', include('apps.admin_panel.urls')),
    
    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Robots.txt
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

# Add media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns

# Error pages
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'
handler403 = 'apps.core.views.custom_403'