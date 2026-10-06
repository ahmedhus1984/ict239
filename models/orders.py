from __init__ import db
from datetime import datetime, timezone


class OrderItem(db.EmbeddedDocument):
    product = db.ReferenceField('Product')   # ← new — links review back to product
    product_name = db.StringField()
    qty = db.IntField()
    special_price = db.FloatField()
    usual_price = db.FloatField()
    image_url = db.StringField()


class Order(db.Document):
    meta = {'collection': 'orders'}
    user = db.ReferenceField('User')
    items = db.EmbeddedDocumentListField(OrderItem)
    checkout_date = db.DateTimeField(default=lambda: datetime.now(timezone.utc))
    total = db.FloatField(default=0)

    @staticmethod
    def createOrder(user, cart):
        order_items = []
        total = 0

        for item in cart.items:
            if not item.product:
                continue
            order_items.append(OrderItem(
                product=item.product,
                product_name=item.product.name,
                qty=item.qty,
                special_price=item.product.special_price,
                usual_price=item.product.usual_price,
                image_url=item.product.image_url
            ))
            total += item.product.special_price * item.qty

        order = Order(
            user=user,
            items=order_items,
            total=total
        ).save()
        return order

    @staticmethod
    def getUserOrders(user):
        return Order.objects(user=user).order_by('-checkout_date')