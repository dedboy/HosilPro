from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # auction_id bu yerda integer (\d+) bo'lishi kerak
    re_path(r'ws/auction/(?P<auction_id>\d+)/$', consumers.AuctionConsumer.as_asgi()),
]