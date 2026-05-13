from .models import Notification
from .models import Wallet


def wallet_balance(request):
    if request.user.is_authenticated:
        wallet, _ = Wallet.objects.get_or_create(user=request.user)
        return {'wallet': wallet}
    return {'wallet': None}

def notifications_count(request):
    if request.user.is_authenticated:
        # Faqat o'qilmagan xabarlar soni
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}