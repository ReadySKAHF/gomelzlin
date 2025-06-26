from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [

    # Корзина
    path('cart/', views.CartView.as_view(), name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('cart/update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('cart/preview/', views.cart_preview_ajax, name='cart_preview_ajax'),
    path('cart/quick-add/', views.quick_add_to_cart, name='quick_add_to_cart'),
    
    # Оформление заказа
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Заказы
    path('orders/', views.OrderListView.as_view(), name='order_list'),
    path('order/<str:number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('order/<str:number>/cancel/', views.cancel_order, name='cancel_order'),
]