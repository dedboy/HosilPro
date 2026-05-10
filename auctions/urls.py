from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('my-participation/', views.my_bids, name='my_bids'),
    path('categories/', views.category_list, name='category_list'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # MANA BU ENG MUHIM QATOR:
    path('/profile/', views.profile_view, name='profile'),
    path('notifications/read-all/', views.mark_all_as_read, name='mark_all_read'),
    path('notifications/mark-read/', views.mark_all_as_read, name='mark_all_read'),
]