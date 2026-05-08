from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from .forms import UserRegisterForm
from auctions.models import Product, Bid


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Hisob yaratildi: {username}! Endi kirishingiz mumkin.")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # 1. Foydalanuvchi o'zi sotuvga qo'ygan mahsulotlar
    my_products = Product.objects.filter(owner=request.user).order_by('-created_at')

    # 2. Foydalanuvchi yutib olgan auksionlar
    won_products = Product.objects.filter(winner=request.user).order_by('-end_time')

    # 3. Foydalanuvchi narx urgan barcha auksionlar (tarixi)
    # Bu qism foydalanuvchi qaysi auksionlarda qatnashayotganini ko'rsatadi
    my_bids = Bid.objects.filter(user=request.user).select_related('product').order_by('-timestamp')

    # 4. Statistika (Fermerlar va faol foydalanuvchilar uchun)
    stats = {
        'total_auctions': my_products.count(),  # Jami qo'shgan e'lonlari
        'active_auctions': my_products.filter(end_time__gt=timezone.now()).count(),  # Hali tugamagan e'lonlari
        'total_bids_received': Bid.objects.filter(product__owner=request.user).count(),
        # Uning mahsulotlariga kelgan takliflar soni
        'won_count': won_products.count(),  # Yutib olganlari soni
    }

    context = {
        'my_products': my_products,
        'won_products': won_products,
        'my_bids': my_bids,
        'stats': stats,
    }

    return render(request, 'users/profile.html', context)