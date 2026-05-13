from django import forms
from .models import Product, ProductImage
from django.forms import inlineformset_factory
from django import forms

class DepositForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=1000, label="To'ldirish summasi")

class WithdrawForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2, min_value=10000, label="Yechish summasi")

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'category', 'description', 'image', 'location', 'start_price', 'end_time']
        widgets = {
            # HTML5 datetime-local fermerlar uchun qulayroq
            'end_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control', 'id': 'auction_end_time'}),
            # Tavsif maydonini biroz kichraytiramiz
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                                 'placeholder': 'Mahsulot haqida qo\'shimcha ma\'lumot (ixtiyoriy)'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # 2-tavsiya: Tavsifni ixtiyoriy (Optional) qilish
        self.fields['description'].required = False

        # 4-tavsiya: Narx maydoniga faqat musbat sonlar cheklovi
        self.fields['start_price'].widget = forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '0',
            'step': '1000',
            'placeholder': 'Faqat sonlar (masalan: 50000)'
        })


ProductImageFormSet = inlineformset_factory(
    Product, ProductImage, fields=('image',), extra=3, can_delete=True
)