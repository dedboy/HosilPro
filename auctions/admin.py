from django.contrib import admin
from .models import Category, Product, ProductImage, Bid

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3 # Bir vaqtda 3 tagacha rasm joyini chiqarib turadi

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'start_price', 'current_price', 'end_time', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [ProductImageInline] # Rasmlarni mahsulot ichida chiqaradi

admin.site.register(Category)
admin.site.register(Bid)