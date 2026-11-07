from models.users import User
from models.hotels import Hotel
from models.package import Package
from __init__ import db
from mongoengine import ListField, DictField
from mongoengine.queryset.visitor import Q
from mongoengine.errors import ValidationError
from datetime import datetime # Make sure this is imported at the top
import random
from models.attractions import Attraction

class Booking(db.Document):
  meta = {'collection': 'booking'}

  check_in_date = db.DateTimeField(required=True)
  check_out_date = db.DateTimeField()  # Required for Hotel bookings, None/optional for Package
  customer = db.ReferenceField(User, required=True)
  hotel = db.ReferenceField(Hotel, default=None)
  package = db.ReferenceField(Package, default=None)
  total_cost = db.FloatField()
  holiday_type = db.StringField() # <-- ADDED THIS
  itinerary = db.ListField(db.DictField()) # <-- ADD THIS

  def clean(self):
    """Enforce XOR constraint: must reference EITHER a hotel OR a package, never both or neither."""
    if (self.hotel is None and self.package is None) or (self.hotel is not None and self.package is not None):
        raise ValidationError("Booking must reference either a Hotel or a Package, but not both or neither.")

    # Ensure hotel bookings have a check_out_date
    if self.hotel is not None:
      if self.check_out_date is None:
        raise ValidationError("Hotel bookings require a check-out date.")
      if self.check_out_date <= self.check_in_date:
        raise ValidationError("Check-out date must be after the check-in date.")

  def calculate_total_cost(self, nights=1):
      if self.package:
          self.total_cost = self.package.package_cost
      elif self.hotel and self.check_out_date:
          # By this point, the dates should already be datetime objects
          nights = (self.check_out_date - self.check_in_date).days
          self.total_cost = self.hotel.est_nightly_price * nights
          
      self.save()

  @staticmethod
  def createBooking(check_in_date, check_out_date, customer, hotel=None, package=None, nights=1, holiday_type=None):

    # Convert strings to datetime before passing to MongoEngine
    if isinstance(check_in_date, str) and check_in_date:
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d')
    if isinstance(check_out_date, str) and check_out_date:
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d')

    booking = Booking(
      check_in_date=check_in_date,
      check_out_date=check_out_date,
      customer=customer,
      hotel=hotel,
      package=package,
      holiday_type=holiday_type
    )
    booking.clean()
    booking.save()
    booking.calculate_total_cost(nights=nights)
    return booking

  @staticmethod
  def getBookingsByEmail(email):
    customer = User.getUser(email)
    if customer:
        return Booking.objects(customer=customer)
    return []


  @staticmethod
  def getAllBookings():
    return Booking.objects()

  @staticmethod
  def getUserBookingsFromDate(customer, from_date):
    return Booking.objects(Q(customer = customer) & Q(check_in_date__gte = from_date))

  @staticmethod
  def updateBooking(old_check_in_date, new_check_in_date, customer, hotel_name=None, package_title=None, new_check_out_date=None):
      from datetime import datetime, timedelta
      
      booking = Booking.getBooking(old_check_in_date, customer, hotel_name=hotel_name, package_title=package_title)
      
      if booking:
        # 1. Convert dates to datetime objects if they are strings
        current_check_in = booking.check_in_date
        if isinstance(current_check_in, str):
            current_check_in = datetime.strptime(current_check_in, '%Y-%m-%d')
            
        if isinstance(new_check_in_date, str):
            new_check_in = datetime.strptime(new_check_in_date, '%Y-%m-%d')
        else:
            new_check_in = new_check_in_date

        # 2. Block updates for past bookings
        if current_check_in.date() < datetime.now().date():
            return None

        # 3. If a new check-out date is provided (Hotel only)
        if new_check_out_date and booking.hotel:
            if isinstance(new_check_out_date, str):
                new_check_out = datetime.strptime(new_check_out_date, '%Y-%m-%d')
            else:
                new_check_out = new_check_out_date
                
            booking.check_in_date = new_check_in
            booking.check_out_date = new_check_out
            
        # 4. If NO check-out date is provided, but it's a hotel, shift the check-out date
        elif not new_check_out_date and booking.hotel and booking.check_out_date:
            old_check_out = booking.check_out_date
            if isinstance(old_check_out, str):
                old_check_out = datetime.strptime(old_check_out, '%Y-%m-%d')
                
            # Calculate original duration and shift check-out
            duration = (old_check_out - current_check_in).days
            booking.check_in_date = new_check_in
            booking.check_out_date = new_check_in + timedelta(days=duration)
            
        # 5. For packages, just update the check-in date
        else:
            booking.check_in_date = new_check_in

        # Validate dates before saving
        if booking.hotel and booking.check_out_date <= booking.check_in_date:
            raise ValidationError("Check-out date must be after the check-in date.")

        # Recalculate cost and save
        booking.calculate_total_cost()
        return booking.save()
        
      return None

  @staticmethod
  def getBooking(check_in_date, customer, hotel_name=None, package_title=None):
    query = Q(customer=customer) & Q(check_in_date=check_in_date)
    if package_title:
        package = Package.objects(title=package_title).first() 
        query &= Q(package=package)
    elif hotel_name:
        hotel = Hotel.getHotel(hotel_name)
        query &= Q(hotel=hotel)
    return Booking.objects(query).first()

  def getItinerary(self):
    import random
    from models.attractions import Attraction

    if self.hotel:
        neighborhood = self.hotel.neighborhood.strip('"')
    elif self.package:
        neighborhood = self.package.neighborhood.strip('"')
    else:
        return []

    holiday_type = self.holiday_type.strip('"')

    # 1. Fetch Primary Attractions (Morning/Afternoon)
    if holiday_type == "Food":
        primary_attractions = Attraction.objects(neighborhood=neighborhood, category="Food")
    else:
        primary_attractions = Attraction.objects(category=holiday_type)

    # 2. Fetch Food Attractions for Evening (Only for Nature)
    evening_food_attractions = []
    if holiday_type == "Nature":
        evening_food_attractions = Attraction.objects(neighborhood=neighborhood, category="Food")

    morning_list = []
    afternoon_list = []
    evening_list = []

    for attr in primary_attractions:
        if attr.time_slot:
            slots = [s.strip('"') for s in attr.time_slot]
            if "Morning" in slots: morning_list.append(attr)
            if "Afternoon" in slots: afternoon_list.append(attr)
            if holiday_type != "Nature" and "Evening" in slots: evening_list.append(attr)

    if holiday_type == "Nature":
        for food_attr in evening_food_attractions:
            if food_attr.time_slot:
                slots = [s.strip('"') for s in food_attr.time_slot]
                if "Evening" in slots: evening_list.append(food_attr)

    duration = 1
    if self.package:
        duration = self.package.duration
    elif self.hotel and self.check_out_date:
        duration = (self.check_out_date - self.check_in_date).days

    # 3. Build the itinerary list
    itinerary = []
    
    for day in range(1, duration + 1):
        day_plan = {"day": day, "morning": None, "afternoon": None, "evening": None}

        def build_slot(attraction_list):
            if not attraction_list:
                return None
            chosen = random.choice(attraction_list)
            alternatives = [a for a in attraction_list if a.id != chosen.id]
            return {
                "chosen": chosen,
                "alternatives": alternatives
            }

        day_plan["morning"] = build_slot(morning_list)
        day_plan["afternoon"] = build_slot(afternoon_list)
        day_plan["evening"] = build_slot(evening_list)

        itinerary.append(day_plan)

    # 4. Save to database and return
    self.itinerary = itinerary
    self.save()

    return itinerary

  @staticmethod
  def getDashboardData():
    all_bookings = list(Booking.objects())
    today = datetime.now()

    # 1. Stat Cards
    total_bookings = len(all_bookings)
    upcoming_bookings = 0
    total_revenue = 0.0
    unique_hotels = set()

    for b in all_bookings:
        try:
            # Upcoming check
            if b.check_in_date and b.check_in_date.date() >= today.date():
                upcoming_bookings += 1
            # Revenue check
            if b.total_cost:
                total_revenue += b.total_cost
            # Unique hotels check
            if b.hotel:
                unique_hotels.add(b.hotel.hotel_name)
            elif b.package:
                unique_hotels.add(b.package.hotel_name)
        except Exception:
            continue

    # 2. Grouping Dictionaries
    bookings_by_month = {}
    revenue_by_month = {}
    booking_type_mix = {"Hotel": 0, "Package": 0}
    holiday_type_mix = {"Family": 0, "Food": 0, "Nature": 0}
    top_hotels = {}
    neighborhood_bookings = {}
    itinerary_activity_count = {}

    for b in all_bookings:
        try:
            # Month Processing
            if b.check_in_date:
                month_str = b.check_in_date.strftime("%Y-%m")
                bookings_by_month[month_str] = bookings_by_month.get(month_str, 0) + 1
                
                if b.total_cost:
                    revenue_by_month[month_str] = revenue_by_month.get(month_str, 0) + b.total_cost

            # Type Mix & Neighborhood
            hotel_name = "Unknown"
            neighborhood = "Unknown"

            if b.hotel:
                booking_type_mix["Hotel"] += 1
                hotel_name = b.hotel.hotel_name.strip('"')
                neighborhood = b.hotel.neighborhood.strip('"')
            elif b.package:
                booking_type_mix["Package"] += 1
                hotel_name = b.package.hotel_name.strip('"')
                neighborhood = b.package.neighborhood.strip('"')

            if hotel_name != "Unknown":
                top_hotels[hotel_name] = top_hotels.get(hotel_name, 0) + 1
                neighborhood_bookings[neighborhood] = neighborhood_bookings.get(neighborhood, 0) + 1

            # Holiday Type Mix
            if b.holiday_type:
                h_type = b.holiday_type.strip('"')
                if h_type in holiday_type_mix:
                    holiday_type_mix[h_type] += 1

            # Activities Count inside Itinerary
            if b.itinerary:
                for day in b.itinerary:
                    if not isinstance(day, dict):
                        continue
                        
                    for slot in ["morning", "afternoon", "evening"]:
                        slot_data = day.get(slot)
                        if isinstance(slot_data, dict) and slot_data.get("chosen"):
                            attraction = slot_data["chosen"]
                            
                            if hasattr(attraction, 'fetch'):
                                attraction = attraction.fetch()
                                
                            if attraction and hasattr(attraction, 'name'):
                                attraction_name = attraction.name.strip('"')
                                itinerary_activity_count[attraction_name] = itinerary_activity_count.get(attraction_name, 0) + 1
                                
        except Exception as e:
            print(f"Error processing booking {b.id}: {e}")
            continue

    # 3. Sort Data
    sorted_months = sorted(bookings_by_month.keys())
    sorted_bookings_month = [{"month": m, "count": bookings_by_month[m]} for m in sorted_months]
    sorted_revenue_month = [{"month": m, "revenue": round(revenue_by_month.get(m, 0), 2)} for m in sorted_months]
    
    sorted_top_hotels = [{"hotel": k, "count": v} for k, v in sorted(top_hotels.items(), key=lambda item: item[1], reverse=True)[:5]]
    sorted_neighborhoods = [{"neighborhood": k, "count": v} for k, v in sorted(neighborhood_bookings.items(), key=lambda item: item[1], reverse=True)]
    sorted_activities = [{"activity": k, "count": v} for k, v in sorted(itinerary_activity_count.items(), key=lambda item: item[1], reverse=True)[:8]]

    return {
        "stats": {
            "total_bookings": total_bookings,
            "upcoming_bookings": upcoming_bookings,
            "total_revenue": round(total_revenue, 2),
            "hotels_with_bookings": len(unique_hotels)
        },
        "bookings_by_month": sorted_bookings_month,
        "revenue_by_month": sorted_revenue_month,
        "booking_type_mix": booking_type_mix,
        "holiday_type_mix": holiday_type_mix,
        "top_hotels": sorted_top_hotels,
        "bookings_by_neighborhood": sorted_neighborhoods,
        "most_suggested_activities": sorted_activities
    }