from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('product/create/', views.product_create, name='product_create'),  # ← yuqoriga ko'chdi
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.product_update, name='product_update'),
    path('product/<int:pk>/delete/', views.product_delete, name='product_delete'),

    path('categories/', views.category_list, name='category_list'),
    path('my-participation/', views.my_bids, name='my_bids'),

    # profile/ o'chirildi — users/urls.py da bor
    path('deposit/', views.deposit_view, name='deposit_view'),
    path('withdraw/', views.withdraw_view, name='withdraw_view'),

    path('notifications/read-all/', views.mark_all_as_read, name='mark_all_read'),
]