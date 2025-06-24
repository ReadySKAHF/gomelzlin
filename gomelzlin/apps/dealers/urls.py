from django.urls import path
from . import views

app_name = 'dealers'

urlpatterns = [
    path('', views.DealerListView.as_view(), name='dealer_list'),
    path('<int:pk>/', views.DealerDetailView.as_view(), name='dealer_detail'),
]