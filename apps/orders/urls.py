from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Корзина
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('update/', views.UpdateCartView.as_view(), name='update_cart'),
    path('remove/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('clear/', views.clear_cart_view, name='clear_cart'),
    
    # Заказы
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('order/<str:number>/', views.OrderDetailView.as_view(), name='order_detail'),
]