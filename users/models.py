from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Viloyatlar ro'yxati (choices)
    REGION_CHOICES = [
        ('toshkent', 'Toshkent'),
        ('samarqand', 'Samarqand'),
        ('fargona', 'Farg\'ona'),
        ('andijon', 'Andijon'),
        ('namangan', 'Namangan'),
        ('buxoro', 'Buxoro'),
        ('navoiy', 'Navoiy'),
        ('qashqadaryo', 'Qashqadaryo'),
        ('surxondaryo', 'Surxondaryo'),
        ('xorazm', 'Xorazm'),
        ('jizzax', 'Jizzax'),
        ('sirdaryo', 'Sirdaryo'),
        ('qoraqalpogiston', 'Qoraqalpog\'iston'),
    ]

    is_farmer = models.BooleanField(default=False, verbose_name="Fermermi?")
    is_restaurant = models.BooleanField(default=False, verbose_name="Restoranmi?")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Telefon raqami")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, blank=True, null=True, verbose_name="Viloyat")

    def __str__(self):
        return self.username