from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Product, Bid
from .forms import ProductCreateForm


def product_list(request):
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    return render(request, 'auctions/product_list.html', {'products': products})


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    bids = product.bids.all().order_by('-amount')

    # Auksion vaqti tugaganini tekshirish
    is_finished = product.end_time < timezone.now()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Narx taklif qilish uchun tizimga kiring!")
            return redirect('login')

        if is_finished:
            messages.error(request, "Auksion vaqti tugagan!")
            return redirect('product_detail', pk=pk)

        amount = request.POST.get('bid_amount')
        if amount:
            amount = float(amount)
            current_price = product.current_price if product.current_price else product.start_price

            if amount > current_price:
                Bid.objects.create(product=product, user=request.user, amount=amount)
                product.current_price = amount
                product.save()
                messages.success(request, "Sizning taklifingiz qabul qilindi!")
            else:
                messages.error(request, "Taklif joriy narxdan yuqori bo'lishi kerak!")

        return redirect('product_detail', pk=pk)

    return render(request, 'auctions/product_detail.html', {
        'product': product,
        'bids': bids,
        'is_finished': is_finished,
        'now': timezone.now()
    })


@login_required
def product_create(request):
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