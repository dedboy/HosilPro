from .models import Notification

def notifications_count(request):
    if request.user.is_authenticated:
        # Faqat o'qilmagan xabarlar soni
        count = Notification.objects.filter(recipient=request.user, is_read=False).count()
        return {'unread_count': count}
    return {'unread_count': 0}