from django.contrib import admin
from .models import Category, Product, Bid

admin.site.register(Category)
admin.site.register(Product)

admin.site.register(Bid)