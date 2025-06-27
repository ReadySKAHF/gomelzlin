# from django.urls import path
# from . import views

# app_name = 'orders'

# urlpatterns = [

#     # Корзина
#     path('cart/', views.CartView.as_view(), name='cart'),
#     path('cart/add/', views.add_to_cart, name='add_to_cart'),
#     path('cart/update/', views.update_cart_item, name='update_cart_item'),
#     path('cart/update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
#     path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
#     path('cart/clear/', views.clear_cart, name='clear_cart'),
#     path('cart/count/', views.get_cart_count, name='get_cart_count'),
#     path('cart/preview/', views.cart_preview_ajax, name='cart_preview_ajax'),
#     path('cart/quick-add/', views.quick_add_to_cart, name='quick_add_to_cart'),
    
#     # Оформление заказа
#     path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
#     # Заказы
#     path('orders/', views.OrderListView.as_view(), name='order_list'),
#     path('order/<str:number>/', views.OrderDetailView.as_view(), name='order_detail'),
#     path('order/<str:number>/cancel/', views.cancel_order, name='cancel_order'),
# ]

# apps/orders/urls.py
from django.urls import path
from . import views

# Убираем app_name, так как namespace указан в основном urls.py

urlpatterns = [
    # Корзина (доступна через /cart/)
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.add_to_cart, name='add_to_cart'),
    path('update/', views.update_cart_item, name='update_cart_item'),
    path('update-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    path('remove/', views.remove_from_cart, name='remove_from_cart'),
    path('clear/', views.clear_cart, name='clear_cart'),
    path('count/', views.get_cart_count, name='get_cart_count'),
    path('preview/', views.cart_preview_ajax, name='cart_preview_ajax'),
    path('quick-add/', views.quick_add_to_cart, name='quick_add_to_cart'),
    
    # Оформление заказа (доступно через /orders/)
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # Заказы (доступно через /orders/)
    path('list/', views.OrderListView.as_view(), name='order_list'),
    path('<str:number>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<str:number>/cancel/', views.cancel_order, name='cancel_order'),
    
    # Избранное (wishlist)
    path('wishlist/add/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('wishlist/status/', views.get_wishlist_status, name='get_wishlist_status'),
    path('wishlist/count/', views.wishlist_count, name='wishlist_count'),
]