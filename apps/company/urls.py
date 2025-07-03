from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('leadership/', views.LeadershipView.as_view(), name='leadership'),
    path('partners/', views.PartnersView.as_view(), name='partners'),
]