from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        # Modelda bor maydonlarni ko'rsatamiz:
        fields = ('username', 'phone_number', 'region', 'is_farmer', 'is_restaurant')