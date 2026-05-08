from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('my-participation/', views.my_bids, name='my_bids'), # Yangi!
    path('categories/', views.category_list, name='category_list'), # Yangi!
]