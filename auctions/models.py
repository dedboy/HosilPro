from django.db import models
from django.conf import settings
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    description = models.TextField(verbose_name="Batafsil ma'lumot")
    image = models.ImageField(upload_to='products/', verbose_name="Rasm")

    # Auksion shartlari
    start_price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Boshlang'ich narx")
    current_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_price(self):
        # Eng baland narxni topish
        highest_bid = self.bids.order_by('-amount').first()
        if highest_bid:
            self.current_price = highest_bid.amount
            self.save()
    def __str__(self):
        return self.title

class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Taklif qilingan narx")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} ({self.product.title})"

    class Meta:
        ordering = ['-amount']  # Eng baland narx har doim tepada tursin