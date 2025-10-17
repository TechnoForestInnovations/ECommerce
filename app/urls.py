from django.urls import path
from . import views


urlpatterns = [
    path('home_view/', views.home_view, name='home_view'),
    path('landing_view/', views.landing_view, name='landing_view'),
    path('products/', views.product_list, name='product_list'),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
]
