from django.contrib import admin
from .models import Category, Product, ProductImage, Bid, Wallet, Transaction

# --- HAMYON VA TRANZAKSIYALAR ---

class TransactionInline(admin.TabularInline):
    model = Transaction
    extra = 0
    readonly_fields = ('amount', 'transaction_type', 'description', 'created_at')
    can_delete = False

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'frozen_balance', 'get_available_balance_display')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('frozen_balance',)
    inlines = [TransactionInline]

    def get_available_balance_display(self, obj):
        return obj.get_available_balance()
    get_available_balance_display.short_description = "Ishlatish mumkin bo'lgan balans"

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('wallet__user__username', 'description')

# --- MAHSULOT VA AUKSION ---

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'start_price', 'current_price', 'end_time', 'is_active')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    inlines = [ProductImageInline]

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__title', 'user__username')

admin.site.register(Category)