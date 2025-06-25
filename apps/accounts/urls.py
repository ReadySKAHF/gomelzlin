from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
]

# apps/core/urls.py (исправленный)
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
]

# apps/company/urls.py (исправленный)
from django.urls import path
from . import views

app_name = 'company'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('leadership/', views.LeadershipView.as_view(), name='leadership'),
    path('partners/', views.PartnersView.as_view(), name='partners'),
    path('policies/', views.PoliciesView.as_view(), name='policies'),
]