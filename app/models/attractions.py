from __init__ import db

class Attraction(db.Document):
    meta = {'collection': 'attractions'}

    name = db.StringField(required=True)
    category = db.StringField()
    time_slot = db.ListField(db.StringField())
    neighborhood = db.StringField()
    is_free = db.BooleanField(default=False)
    cost_range = db.StringField()
    michelin_award = db.StringField()
    signature_dish = db.StringField()
    opening_time = db.StringField()
    closing_time = db.StringField()
    details = db.StringField()
    address = db.StringField()
    image_url = db.StringField()

    @staticmethod
    def getAttraction(name):
        return Attraction.objects(name=name).first()

    @staticmethod
    def getAllAttractions():
        return Attraction.objects()