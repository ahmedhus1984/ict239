from __init__ import db


class CartItem(db.EmbeddedDocument):
    product = db.ReferenceField('Product')
    qty = db.IntField(default=1)


class Cart(db.Document):
    meta = {'collection': 'carts'}
    user = db.ReferenceField('User')
    items = db.EmbeddedDocumentListField(CartItem)

    @staticmethod
    def getCart(user):
        cart = Cart.objects(user=user).first()
        if not cart:
            cart = Cart(user=user, items=[]).save()
        return cart

    @staticmethod
    def addItem(user, product, qty=1):
        cart = Cart.getCart(user)
        for item in cart.items:
            if item.product and item.product.id == product.id:
                item.qty += qty
                cart.save()
                return cart
        cart.items.append(CartItem(product=product, qty=qty))
        cart.save()
        return cart

    @staticmethod
    def updateQty(user, product_id, qty):
        cart = Cart.getCart(user)
        for item in cart.items:
            if item.product and str(item.product.id) == str(product_id):
                if qty <= 0:
                    cart.items.remove(item)
                else:
                    item.qty = qty
                cart.save()
                return cart
        return cart

    @staticmethod
    def removeItem(user, product_id):
        cart = Cart.getCart(user)
        for item in cart.items:
            if item.product and str(item.product.id) == str(product_id):
                cart.items.remove(item)
                break
        cart.save()
        return cart

    def grandTotal(self):
        total = 0
        for item in self.items:
            if item.product:
                total += item.product.special_price * item.qty
        return total