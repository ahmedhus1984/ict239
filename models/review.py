from __init__ import db
from datetime import datetime, timezone


class Review(db.Document):
    meta = {
        'collection': 'reviews',
        'indexes': [
            {'fields': ['user', 'product'], 'unique': True}   # one review per user per product
        ]
    }
    user = db.ReferenceField('User')
    product = db.ReferenceField('Product')
    rating = db.IntField(min_value=1, max_value=5)
    text = db.StringField(max_length=1000)
    date = db.DateTimeField(default=lambda: datetime.now(timezone.utc))

    @staticmethod
    def getReview(user, product):
        return Review.objects(user=user, product=product).first()

    @staticmethod
    def addOrUpdate(user, product, rating, text):
        review = Review.getReview(user, product)
        if review:
            review.rating = rating
            review.text = text
            review.date = datetime.now(timezone.utc)
        else:
            review = Review(user=user, product=product, rating=rating, text=text)
        review.save()
        return review

    @staticmethod
    def getProductReviews(product):
        return Review.objects(product=product).order_by('-date')

    @staticmethod
    def getAverageRating(product):
        reviews = Review.objects(product=product)
        if reviews.count() == 0:
            return None
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    @staticmethod
    def getReviewCount(product):
        return Review.objects(product=product).count()

    @staticmethod
    def getNewestReview(product):
        return Review.objects(product=product).order_by('-date').first()