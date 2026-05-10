from django import forms
from .models import Product, ProductImage
from django.forms import inlineformset_factory

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'title', 'description', 'image', 'location', 'start_price', 'end_time']
        widgets = {
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

ProductImageFormSet = inlineformset_factory(
    Product, ProductImage, fields=('image',), extra=3, can_delete=True
)