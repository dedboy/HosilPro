from django.urls import path
from . import views

urlpatterns = [
    # Mahsulotlar va Auksion
    path('', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/create/', views.product_create, name='product_create'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    # Kategoriyalar va Ishtirok
    path('categories/', views.category_list, name='category_list'),
    path('my-participation/', views.my_bids, name='my_bids'),

    # Profil va Hamyon (Wallet)
    path('profile/', views.profile_view, name='profile'),
    path('deposit/', views.deposit_view, name='deposit_view'),  # views.py dagi nomga moslandi
    path('withdraw/', views.withdraw_view, name='withdraw_view'),

    # Bildirishnomalar
    path('notifications/read-all/', views.mark_all_as_read, name='mark_all_read'),
]