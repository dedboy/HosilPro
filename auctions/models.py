from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True) # Bildirishnoma bosilganda qayerga o'tishi
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} uchun xabar"

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True, help_text="Bootstrap icon klassi")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Kategoriyalar"

class Product(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    description = models.TextField(verbose_name="Batafsil ma'lumot")
    image = models.ImageField(upload_to='products/', verbose_name="Asosiy rasm")
    location = models.CharField(max_length=255, verbose_name="Manzil (Tuman, qishloq)", blank=True)

    start_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="Boshlang'ich narx",
        validators=[MinValueValidator(0)]
    )
    current_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        validators=[MinValueValidator(0)]
    )

    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='won_auctions')

    def get_current_price(self):
        return self.current_price if self.current_price else self.start_price

    def is_finished(self):
        """Auksion vaqti tugaganligini tekshiradi"""
        return timezone.now() > self.end_time

    def determine_winner(self):
        """G'olibni aniqlash funksiyasi"""
        if self.is_finished() and not self.winner:
            # Eng baland narx bergan bidni oladi
            highest_bid = self.bids.order_by('-amount').first()
            if highest_bid:
                self.winner = highest_bid.user
                self.save()
        return self.winner

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')

    def __str__(self):
        return f"{self.product.title} rasmi"

class Bid(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Taklif narxi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']