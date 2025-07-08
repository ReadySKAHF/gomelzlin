from django.urls import path
from . import views

urlpatterns = [
    path('', views.DealerListView.as_view(), name='dealer_list'),
    path('<int:pk>/', views.DealerDetailView.as_view(), name='dealer_detail'),

    # API
    path('api/map-data/', views.dealer_map_data, name='map_data'),
    path('api/regions/', views.dealer_regions, name='regions'),
]