from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login  # Avtomatik kirish uchun
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import UserRegisterForm
from auctions.models import Product, Bid


def register(request):
    # Agar foydalanuvchi allaqachon tizimga kirgan bo'lsa, uni profilga yuboramiz
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Foydalanuvchini saqlaymiz
            username = form.cleaned_data.get('username')

            # Ro'yxatdan o'tgach avtomatik tizimga kiritish (ixtiyoriy, lekin qulay)
            login(request, user)

            messages.success(request, f"Xush kelibsiz, {username}! Hisobingiz muvaffaqiyatli yaratildi.")

            # Agar fermer bo'lsa, mahsulot qo'shishga, aks holda auksionlarga yo'naltiramiz
            if user.is_farmer:
                return redirect('product_create')  # Bu view nomi auctions/urls.py da bo'lishi kerak
            return redirect('product_list')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # 1. Foydalanuvchi o'zi sotuvga qo'ygan mahsulotlar
    my_products = Product.objects.filter(owner=request.user).order_by('-created_at')

    # 2. Foydalanuvchi yutib olgan auksionlar (winner maydoni mahsulotda bo'lishi kerak)
    # Ba'zan modelda winner maydoni bo'lmasligi mumkin, shuni tekshirib ko'ring
    won_products = Product.objects.filter(winner=request.user).order_by('-end_time')

    # 3. Foydalanuvchi narx urgan barcha auksionlar (tarixi)
    # select_related bazaga so'rovni kamaytiradi (Optimization)
    my_bids = Bid.objects.filter(user=request.user).select_related('product').order_by('-created_at')

    # 4. Statistika
    now = timezone.now()
    stats = {
        'total_auctions': my_products.count(),
        'active_auctions': my_products.filter(end_time__gt=now).count(),
        'total_bids_received': Bid.objects.filter(product__owner=request.user).count(),
        'won_count': won_products.count(),
    }

    context = {
        'my_products': my_products,
        'won_products': won_products,
        'my_bids': my_bids,
        'stats': stats,
    }

    return render(request, 'users/profile.html', context)