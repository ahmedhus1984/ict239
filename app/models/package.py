import re
from __init__ import db

class Package(db.Document):
    meta = {'collection': 'packages'}

    # Denormalized Hotel attributes
    hotel_name = db.StringField(required=True)
    neighborhood = db.StringField(required=True)
    hotel_class = db.StringField(required=True)
    est_nightly_price = db.FloatField(required=True)
    description = db.StringField(max_length=500)
    address = db.StringField()
    amenities = db.ListField(db.StringField())
    image_url = db.StringField()

    # Package-specific attributes
    title = db.StringField(required=True)
    duration = db.IntField(required=True)
    original_price = db.FloatField(required=True)
    discount = db.FloatField(required=True)
    package_cost = db.FloatField(required=True)


    def packageCost(self):
      return self.package_cost
    
    @staticmethod
    def getPackage(hotel_name):
        # Remove any quotes or extra spaces from the URL input
        clean_name = hotel_name.strip('"\' ')
        
        # Escape special characters (like parentheses) so the regex doesn't break
        safe_name = re.escape(clean_name)
        
        # Build the regex: optional quotes, optional spaces, the name, optional spaces, optional quotes
        query = r'^"?\s*' + safe_name + r'\s*"?$'
        
        # Use iregex to ignore case-sensitivity
        return Package.objects(hotel_name__iregex=query).first()
        
    @staticmethod
    def getAllPackages():
        return Package.objects()

    @staticmethod
    def createPackage(hotel_name, neighborhood, hotel_class, est_nightly_price, description, address, amenities, image_url, title, duration, discount):
        orig_price = est_nightly_price * duration
        pkg_cost = orig_price * (1 - (discount / 100.0))
        return Package(
            hotel_name=hotel_name,
            neighborhood=neighborhood,
            hotel_class=hotel_class,
            est_nightly_price=est_nightly_price,
            description=description,
            address=address,
            amenities=amenities,
            image_url=image_url,
            title=title,
            duration=duration,
            original_price=orig_price,
            discount=discount,
            package_cost=pkg_cost
        ).save()