from django.urls import path
from . import views




urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('update-cart/', views.update_cart_quantity, name='update_cart'),
    path('remove_cart/', views.remove_cart_item, name='remove_cart'),
]