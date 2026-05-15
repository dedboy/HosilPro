from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
# --- HAMYON TIZIMI MODELLARI ---

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Joriy balans"
    )
    frozen_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0.00,
        verbose_name="Muzlatilgan summa"
    )

    def __str__(self):
        return f"{self.user.username} hamyoni - {self.balance} so'm"

    def get_available_balance(self):
        """Ishlatish mumkin bo'lgan sof balans"""
        return self.balance - self.frozen_balance

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('deposit', 'Pul tushirish'),
        ('withdraw', 'Pul yechish'),
        ('payment', 'To\'lov'),
        ('hold', 'Bloklash (Auksion uchun)'),
        ('refund', 'Qaytarish'),
    )

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username} - {self.transaction_type} - {self.amount}"

# --- AUKSION TIZIMI MODELLARI ---

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
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
        return timezone.now() > self.end_time

    def determine_winner(self):
    if self.is_finished() and not self.winner:
        highest_bid = self.bids.order_by('-amount').first()
        if highest_bid:
            with transaction.atomic():
                self.winner = highest_bid.user
                self.save()

                # G'olibning muzlatilgan pulini yechish
                winner_wallet, _ = Wallet.objects.get_or_create(user=highest_bid.user)
                winner_wallet.balance -= highest_bid.amount
                winner_wallet.frozen_balance -= highest_bid.amount
                winner_wallet.save()

                # Sotuvchiga pul o'tkazish
                owner_wallet, _ = Wallet.objects.get_or_create(user=self.owner)
                owner_wallet.balance += highest_bid.amount
                owner_wallet.save()

                # Tranzaksiyalar yozish
                Transaction.objects.create(
                    wallet=winner_wallet,
                    amount=highest_bid.amount,
                    transaction_type='payment',
                    description=f"'{self.title}' auksioni uchun to'lov"
                )
                Transaction.objects.create(
                    wallet=owner_wallet,
                    amount=highest_bid.amount,
                    transaction_type='deposit',
                    description=f"'{self.title}' auksionidan tushum"
                )

                # Bildirishnomalar
                Notification.objects.create(
                    recipient=highest_bid.user,
                    message=f"Tabriklaymiz! Siz '{self.title}' auksionini yutdingiz!",
                    link=f"/product/{self.pk}/"
                )
                Notification.objects.create(
                    recipient=self.owner,
                    message=f"'{self.title}' auksioni tugadi. {highest_bid.amount} so'm hisobingizga o'tkazildi.",
                    link=f"/product/{self.pk}/"
                )

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

# --- SIGNALLAR (Avtomatik Hamyon yaratish uchun) ---

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    """Yangi user yaratilganda unga Wallet qo'shib qo'yadi"""
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_wallet(sender, instance, **kwargs):
    """User profilidagi o'zgarishda Walletni ham saqlaydi"""
    if hasattr(instance, 'wallet'):
        instance.wallet.save()