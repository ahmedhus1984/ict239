from app import db
from models.users import User

# class Bmi_Measurement(db_Document):
class BMIDAILY(db.Document):
    
    meta = {'collection': 'bmidaily'}
    user = db.ReferenceField(User)
    date = db.DateTimeField()
    numberOfMeasures = db.IntField()
    averageBMI = db.FloatField()
    
    def updatedBMI(self, newBMI):
        return (newBMI + (self.averageBMI * self.numberOfMeasures)) / (self.numberOfMeasures + 1) 
    
    
    @staticmethod
    def getBMIDAILY(user, date):
        return BMIDAILY.objects(user=user, date=date).first()
    
    @staticmethod    
    def getAllBMIDAILYs():
        BMIDAILYs = list(BMIDAILY.objects())
        return sorted(BMIDAILYs, key=lambda bmidaily: bmidaily.user)

    @staticmethod #singleto pattern
    def createBMIDAILY(user, date, numM, aveBMI):
        bmidaily = BMIDAILY.getBMIDAILY(user=user, date=date)
        if not bmidaily:
            bmidaily = BMIDAILY(user=user, date=date, numberOfMeasures=numM, averageBMI=aveBMI).save()
        return bmidaily