from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Product, Bid, Category
from django.db.models import Q, Count

def product_list(request):
    """Asosiy sahifa - mahsulotlar ro'yxati va qidiruv"""
    products = Product.objects.filter(is_active=True).order_by('-created_at')

    query = request.GET.get('search')
    category_id = request.GET.get('category')

    if query:
        products = products.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if category_id:
        products = products.filter(category_id=category_id)

    # DIQQAT: Bu yerda 'now' qo'shildi!
    return render(request, 'auctions/product_list.html', {
        'products': products,
        'categories': Category.objects.all(),
        'now': timezone.now()  # HTMLdagi vaqtni solishtirish uchun shart!
    })


def product_detail(request, pk):
    """Mahsulot haqida to'liq ma'lumot va narx urish mantiqi"""
    product = get_object_or_404(Product, pk=pk)
    is_finished = product.is_finished()
    winner = product.determine_winner()
    bids = product.bids.all().order_by('-amount')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Narx taklif qilish uchun tizimga kiring!")
            return redirect('login')

        if is_finished:
            messages.error(request, "Auksion vaqti tugagan!")
            return redirect('product_detail', pk=pk)

        amount = request.POST.get('bid_amount')
        if amount:
            try:
                amount = float(amount)
                if amount > product.get_current_price():
                    Bid.objects.create(product=product, user=request.user, amount=amount)
                    product.current_price = amount
                    product.save()
                    messages.success(request, "Sizning taklifingiz qabul qilindi!")
                else:
                    messages.error(request, "Taklif joriy narxdan yuqori bo'lishi kerak!")
            except ValueError:
                messages.error(request, "Iltimos, to'g'ri son kiriting!")

        return redirect('product_detail', pk=pk)

    return render(request, 'auctions/product_detail.html', {
        'product': product,
        'bids': bids,
        'is_finished': is_finished,
        'winner': winner,
        'now': timezone.now()
    })


@login_required
def product_create(request):
    """Yangi e'lon qo'shish"""
    from .forms import ProductCreateForm
    if request.method == 'POST':
        form = ProductCreateForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            messages.success(request, "Mahsulot auksionga qo'yildi!")
            return redirect('product_list')
    else:
        form = ProductCreateForm()
    return render(request, 'auctions/product_form.html', {'form': form})


@login_required
def my_bids(request):
    """Foydalanuvchi ishtirok etayotgan auksionlar"""
    user_bids = Bid.objects.filter(user=request.user).select_related('product')
    products_ids = user_bids.values_list('product_id', flat=True).distinct()
    products = Product.objects.filter(id__in=products_ids)

    return render(request, 'auctions/my_bids.html', {
        'products': products,
        'now': timezone.now()  # Bu yerda ham kerak bo'lishi mumkin
    })


def category_list(request):
    """Barcha kategoriyalar ro'yxati"""
    categories = Category.objects.annotate(product_count=Count('product'))
    return render(request, 'auctions/category_list.html', {'categories': categories})