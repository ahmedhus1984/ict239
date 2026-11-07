from flask import Blueprint, render_template
from models.hotels import Hotel

hotel = Blueprint('hotelController', __name__)

@hotel.route('/hotels')
def hotels():
    all_hotels = Hotel.objects()
    return render_template('hotels.html', all_hotels=all_hotels)

@hotel.route("/viewHotelDetail/<hotel_name>")
def viewHotelDetail(hotel_name):
    the_hotel = Hotel.getHotel(hotel_name=hotel_name)
    return render_template('hotelDetail.html', hotel=the_hotel)