from django.urls import path
from .views import product_list, product_detail, product_create

urlpatterns = [
    path('', product_list, name='product_list'),
    path('product/<int:pk>/', product_detail, name='product_detail'),
    path('product/new/', product_create, name='product_create'),
]