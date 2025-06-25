from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order/<str:number>/', views.OrderDetailView.as_view(), name='order_detail'),
]