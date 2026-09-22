from __init__ import db

class Product(db.Document):
    meta = {'collection': 'products'}
    name = db.StringField(max_length=100)
    category = db.StringField(max_length=100)
    special_price = db.FloatField()
    usual_price = db.FloatField()
    stock_qty = db.IntField()
    image_url = db.StringField(max_length=500)
    description = db.StringField(max_length=500)

    def savings(self):
        return self.usual_price - self.special_price

    @staticmethod
    def getProduct(product_id):
      try:
        return Product.objects.get(id=product_id)
      except Product.DoesNotExist:
          return None

    @staticmethod
    def getAllProducts():
        return Product.objects()

    @staticmethod
    def createProduct(name, category, special_price, usual_price, stock_qty, image_url, description):
        return Product(
            name=name,
            category=category,
            special_price=special_price,
            usual_price=usual_price,
            stock_qty=stock_qty,
            image_url=image_url,
            description=description
        ).save()