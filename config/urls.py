from django.contrib import admin
from django.urls import path, include # include ni qo'shish esdan chiqmasin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('auctions.urls')), # Asosiy sahifa va auksionlar
    path('users/', include('users.urls', namespace='users')), # Users appini ulash
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)