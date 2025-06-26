from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('leadership/', views.LeadershipView.as_view(), name='leadership'),
    path('partners/', views.PartnersView.as_view(), name='partners'),
    # Временно закомментированы до создания соответствующих views
    # path('requisites/', views.RequisitesView.as_view(), name='requisites'),
    # path('policies/', views.PoliciesView.as_view(), name='policies'),
    # path('hr-policy/', views.HRPolicyView.as_view(), name='hr_policy'),
    # path('social-policy/', views.SocialPolicyView.as_view(), name='social_policy'),
]