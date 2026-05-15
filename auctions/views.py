from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from django.db import transaction
from decimal import Decimal  # Moliya uchun float o'rniga Decimal shart

from .models import Product, Bid, Category, Notification, Wallet, Transaction
from .forms import ProductForm, ProductImageFormSet, DepositForm, WithdrawForm


# 1. ASOSIY SAHIFA
def product_list(request):
    now = timezone.now()
    products = Product.objects.filter(is_active=True).order_by('-created_at')

    query = request.GET.get('search')
    category_id = request.GET.get('category')

    if query:
        products = products.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, 'auctions/product_list.html', {
        'products': products,
        'categories': Category.objects.all(),
        'now': now
    })


# 2. MAHSULOT QO'SHISH
@login_required
def product_create(request):
    if not getattr(request.user, 'is_farmer', False):
        messages.error(request, "Mahsulot qo'shish uchun 'Dehqon' profili kerak!")
        return redirect('product_list')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        formset = ProductImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            formset.instance = product
            formset.save()
            messages.success(request, "Mahsulot muvaffaqiyatli auksionga qo'yildi!")
            return redirect('product_list')
    else:
        form = ProductForm()
        formset = ProductImageFormSet()
    return render(request, 'auctions/product_form.html', {'form': form, 'formset': formset})


# 3. NARX TAKLIF QILISH (BIDDING)
def product_detail(request, pk):
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

        amount_str = request.POST.get('bid_amount')
        if amount_str:
            try:
                # Katta summalar bilan xatosiz ishlash uchun Decimal
                amount = Decimal(amount_str)

                if amount <= Decimal(str(product.get_current_price())):
                    messages.error(request, "Taklif joriy narxdan yuqori bo'lishi kerak!")
                    return redirect('product_detail', pk=pk)

                user_wallet, _ = Wallet.objects.get_or_create(user=request.user)

                if user_wallet.get_available_balance() < amount:
                    messages.error(request,
                                   f"Mablag' yetarli emas. Balansingiz: {user_wallet.get_available_balance()} so'm")
                    return redirect('deposit_view')

                with transaction.atomic():
                    # Eski taklifni muzlatishdan chiqarish
                    old_highest_bid = product.bids.order_by('-amount').first()
                    if old_highest_bid and old_highest_bid.user != request.user:
                        old_user_wallet, _ = Wallet.objects.get_or_create(user=old_highest_bid.user)
                        old_user_wallet.frozen_balance -= old_highest_bid.amount
                        old_user_wallet.save()

                    # Yangi taklifni muzlatish
                    user_wallet.frozen_balance += amount
                    user_wallet.save()

                    Bid.objects.create(product=product, user=request.user, amount=amount)
                    product.current_price = amount
                    product.save()

                messages.success(request, "Taklif qabul qilindi!")
            except Exception:
                messages.error(request, "Xato summa kiritildi!")

        return redirect('product_detail', pk=pk)

    return render(request, 'auctions/product_detail.html', {
        'product': product, 'bids': bids, 'is_finished': is_finished, 'winner': winner
    })


# 4. DEPOSIT (TO'LDIRISH)
@login_required
@transaction.atomic
def deposit_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            wallet.balance += amount
            wallet.save()

            Transaction.objects.create(
                wallet=wallet, amount=amount,
                transaction_type='deposit', description="Hisob to'ldirildi"
            )

            messages.success(request, f"Hamyoningiz {amount} so'mga to'ldirildi!")
            return redirect('users:profile')
    else:
        form = DepositForm()
    return render(request, 'auctions/deposit.html', {'form': form, 'wallet': wallet})


# 5. WITHDRAW (PUL YECHISH) - TO'G'RILANDI
@login_required
@transaction.atomic
def withdraw_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = WithdrawForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if wallet.get_available_balance() >= amount:
                wallet.balance -= amount
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet, amount=amount,
                    transaction_type='withdraw', description="Mablag' yechib olindi"
                )

                messages.success(request, f"{amount} so'm muvaffaqiyatli yechildi.")
                return redirect('profile')
            else:
                messages.error(request, "Mablag' yetarli emas yoki auksionda muzlatilgan!")
        else:
            # Formadagi validatsiya xatolarini ko'rsatish
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = WithdrawForm()

    return render(request, 'auctions/withdraw.html', {'wallet': wallet, 'form': form})


# 6. PROFIL
@login_required
def profile_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    my_products = Product.objects.filter(owner=request.user).order_by('-created_at')
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]

    return render(request, 'auctions/profile.html', {
        'wallet': wallet,
        'my_products': my_products,
        'notifications': notifications,
    })


# ... Qolgan funksiyalar (update, delete, my_bids, etc.) o'zgarishsiz qoladi ...
# 7. MAHSULOTNI TAHRIRLASH (UPDATE)
@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        formset = ProductImageFormSet(request.POST, request.FILES, instance=product)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Ma'lumotlar muvaffaqiyatli yangilandi!")
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)

    return render(request, 'auctions/product_form.html', {
        'form': form, 'formset': formset, 'is_edit': True
    })

# 8. MAHSULOTNI O'CHIRISH (DELETE)
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if product.owner != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        product.delete()
        messages.success(request, "Mahsulot auksiondan olib tashlandi.")
        return redirect('product_list')

    return render(request, 'auctions/product_confirm_delete.html', {'product': product})

# 9. FOYDALANUVCHI ISHTIROK ETAYOTGAN AUKSIONLAR
@login_required
def my_bids(request):
    user_bids = Bid.objects.filter(user=request.user).select_related('product')
    product_ids = user_bids.values_list('product_id', flat=True).distinct()
    products = Product.objects.filter(id__in=product_ids)

    return render(request, 'auctions/my_bids.html', {
        'products': products,
        'now': timezone.now()
    })

# 10. KATEGORIYALAR RO'YXATI
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('product'))
    return render(request, 'auctions/category_list.html', {'categories': categories})

# 11. BILDIRISHNOMALARNI O'QILDI QILISH
@login_required
def mark_all_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))