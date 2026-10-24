from app import db
from models.users import User

import math

class BMILOG(db.Document):

    meta = {'collection': 'bmilog'}
    user = db.ReferenceField(User)
    datetime = db.DateTimeField()
    weight = db.FloatField()
    height = db.FloatField()
    unit = db.StringField()
    bmi = db.FloatField()
    
    def computeBMI(self):
        if self.unit == 'm':
            bmi = self.weight / math.pow(self.height, 2)
        else:
            bmi = self.weight / math.pow(self.height/100, 2)
        return bmi
    
    @staticmethod
    def getBMILOG(user, datetime):
        return BMILOG.objects(user=user, datetime=datetime).first()
    
    @staticmethod    
    def getAllBMILOGs():
        BMILOGs = list(BMILOG.objects())
        return sorted(BMILOGs, key=lambda bmilog: bmilog.user)

    @staticmethod #singleto pattern
    def createBMILOG(user, datetime, weight, height, unit, bmi):
        bmilog = BMILOG.getBMILOG(user=user, datetime=datetime)
        if not bmilog:
            bmilog = BMILOG(user=user, datetime=datetime, weight=weight, height=height, unit=unit).save()
        return bmilog