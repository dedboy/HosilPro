import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Product, Bid  # Sizdagi model nomlariga qarab


class AuctionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.auction_id = self.scope['url_route']['kwargs']['auction_id']
        self.room_group_name = f'auction_{self.auction_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        bid_amount = data['bid_amount']
        user = self.scope["user"]  # Kim stavka qilganini avtomatik olish

        # 1. Bazada yangi stavkani saqlash
        if user.is_authenticated:
            new_bid = await self.save_bid(self.auction_id, bid_amount, user)

            # 2. Hamma foydalanuvchilarga yangi narxni yuborish
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'auction_message',
                    'bid_amount': str(new_bid.amount),
                    'user': user.username
                }
            )

    @database_sync_to_async
    def save_bid(self, product_id, amount, user):
        product = Product.objects.get(id=product_id)
        # Bazaga saqlash logikasi (masalan, joriy narxdan balandligini tekshirish)
        bid = Bid.objects.create(product=product, user=user, amount=amount)
        product.current_price = amount  # Mahsulot narxini yangilash
        product.save()
        return bid

    async def auction_message(self, event):
        await self.send(text_data=json.dumps({
            'bid_amount': event['bid_amount'],
            'user': event['user']
        }))