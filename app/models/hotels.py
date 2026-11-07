import random
from __init__ import db
from models.package import Package

class Hotel(db.Document):
    meta = {'collection': 'hotels'}

    hotel_name = db.StringField(required=True, unique=True)
    neighborhood = db.StringField(required=True)
    hotel_class = db.StringField(required=True)
    est_nightly_price = db.FloatField(required=True)
    description = db.StringField()
    address = db.StringField()
    amenities = db.ListField(db.StringField())
    image_url = db.StringField()

    @staticmethod
    def getHotel(hotel_name):
        return Hotel.objects(hotel_name=hotel_name).first()

    @staticmethod
    def getAllHotels():
        return Hotel.objects()

    @staticmethod
    def createHotel(hotel_name, neighborhood, hotel_class, est_nightly_price, description, address, amenities, image_url):
      hotel = Hotel(
            hotel_name=hotel_name,
            neighborhood=neighborhood,
            hotel_class=hotel_class,
            est_nightly_price=est_nightly_price,
            description=description,
            address=address,
            amenities=amenities,
            image_url=image_url
        ).save()
    
    
      # 2. Automatically generate 1 to 3 packages for this hotel
      num_packages = random.randint(1, 3)

      # Ensure minimum discount is 5% and maximum is 25%, with increments of 5
      possible_discounts = [5.0, 10.0, 15.0, 20.0, 25.0]

      word=['', '', 'Night Quick Escape', 'Night Signature Stay', 'Night Premium Retreat', 'Night Ultimate Getaway', 'Night Grand Escape', 'Night Elite Retreat']

      

      for i in range(0, num_packages):
        # Pick random distinct durations between 2 and 7 nights
        duration = random.randint(2, 7)
        discount = random.randint(0, 4)
        title = f"{hotel_name} {duration}-{word[duration]}"

        # Use Package model's createPackage method
        Package.createPackage(
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
            discount=possible_discounts[discount]
        )

      return hotel