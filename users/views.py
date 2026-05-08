from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm

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


from auctions.models import Product, Bid
from django.contrib.auth.decorators import login_required


@login_required
def profile(request):
    # O'zi qo'shgan e'lonlar
    my_products = Product.objects.filter(owner=request.user)
    # O'zi narx urgan auksionlar
    my_bids = Bid.objects.filter(user=request.user).order_by('-timestamp')

    return render(request, 'users/profile.html', {
        'my_products': my_products,
        'my_bids': my_bids
    })