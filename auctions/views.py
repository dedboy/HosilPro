from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count
from .models import Product, Bid, Category, Notification  # Notification borligiga ishonch hosil qiling
from .forms import ProductForm, ProductImageFormSet

# 1. MAHSULOTLAR RO'YXATI
def product_list(request):
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
        'now': timezone.now()
    })

# 2. BATAFSIL SAHIFA + BILDIRISHNOMALAR LOGIKASI
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

        amount = request.POST.get('bid_amount')
        if amount:
            try:
                amount = float(amount)
                if amount > product.get_current_price():
                    # Eski eng baland narx bergan odamni saqlab qolamiz
                    old_highest_bid = product.bids.order_by('-amount').first()

                    # Yangi taklifni yaratish
                    Bid.objects.create(product=product, user=request.user, amount=amount)
                    product.current_price = amount
                    product.save()

                    # --- BILDIRISHNOMALAR ---
                    # A. E'lon egasiga xabar yuborish
                    if product.owner != request.user:
                        Notification.objects.create(
                            recipient=product.owner,
                            message=f"Sizning '{product.title}' mahsulotingizga yangi narx taklif qilindi: {amount} so'm",
                            link=f"/product/{product.pk}/"
                        )

                    # B. Avvalgi narx urgan odamga "Sizdan o'zishdi" deb xabar yuborish
                    if old_highest_bid and old_highest_bid.user != request.user:
                        Notification.objects.create(
                            recipient=old_highest_bid.user,
                            message=f"'{product.title}' auksionida sizning taklifingiz mag'lub etildi! Yangi narx: {amount} so'm",
                            link=f"/product/{product.pk}/"
                        )

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

# 3. MAHSULOT QO'SHISH
@login_required
def product_create(request):
    if not request.user.is_farmer:
        messages.error(request, "Mahsulot qo'shish uchun 'Farmer' profili kerak!")
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

# 4. TAHRIRLASH
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
            messages.success(request, "Ma'lumotlar yangilandi!")
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
        formset = ProductImageFormSet(instance=product)
    return render(request, 'auctions/product_form.html', {'form': form, 'formset': formset, 'is_edit': True})

# 5. O'CHIRISH
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if product.owner != request.user:
        raise PermissionDenied
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Mahsulot o'chirildi.")
    return redirect('product_list')

# 6. FOYDALANUVCHI PROFILI
@login_required
def profile_view(request):
    # MAJBURIY YANGILASH: Profil ochilishi bilan hammasini True qilamiz
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    # Keyin ma'lumotlarni bazadan tortamiz
    my_products = Product.objects.filter(owner=request.user).order_by('-created_at')
    my_bids = Bid.objects.filter(user=request.user).select_related('product')
    won_auctions = Product.objects.filter(winner=request.user)
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10]

    return render(request, 'auctions/profile.html', {
        'my_products': my_products,
        'my_bids': my_bids,
        'won_auctions': won_auctions,
        'notifications': notifications,
    })

# 7. KATEGORIYALAR
def category_list(request):
    categories = Category.objects.annotate(product_count=Count('product'))
    return render(request, 'auctions/category_list.html', {'categories': categories})


@login_required
def my_bids(request):
    """Foydalanuvchi taklif bergan mahsulotlar ro'yxati"""
    user_bids = Bid.objects.filter(user=request.user).select_related('product')
    # Faqat taklif berilgan mahsulotlarni bir marta (distinct) olish
    product_ids = user_bids.values_list('product_id', flat=True).distinct()
    products = Product.objects.filter(id__in=product_ids)

    return render(request, 'auctions/my_bids.html', {
        'products': products,
        'now': timezone.now()
    })


@login_required
def mark_all_as_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    # Foydalanuvchi qaysi sahifada turgan bo'lsa, o'sha yerga qaytarish
    referer = request.META.get('HTTP_REFERER')
    if referer:
        return redirect(referer)
    return redirect('product_list')


@login_required
def mark_all_as_read(request):
    """Xabarlarni o'qildi deb belgilab, orqaga qaytaradi"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)

    # Kelgan sahifasiga qaytarish, agar iloji bo'lmasa asosiy sahifaga
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))