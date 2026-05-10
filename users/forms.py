from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegisterForm(UserCreationForm):
    # Telefon raqami uchun qulayroq input
    phone_number = forms.CharField(
        label="Telefon raqami",
        widget=forms.TextInput(attrs={
            'placeholder': '+998901234567',
            'class': 'form-control'
        })
    )

    class Meta:
        model = User
        # Modelda bor maydonlarni ko'rsatamiz:
        fields = ('username', 'phone_number', 'region', 'is_farmer', 'is_restaurant')

        # Har bir maydon uchun Bootstrap klasslarini qo'shib chiqamiz
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'region': forms.Select(attrs={'class': 'form-select'}),
            'is_farmer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_restaurant': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Barcha maydonlarga avtomatik klass qo'shish (agar widget-da berilmagan bo'lsa)
        for field in self.fields:
            if field not in ['is_farmer', 'is_restaurant']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})