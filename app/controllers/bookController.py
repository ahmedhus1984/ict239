from mongoengine.errors import ValidationError
from flask_login import login_user, login_required, logout_user, current_user
from flask import Blueprint, request, redirect, render_template, url_for, flash, jsonify

from models.forms import BookForm
from models.users import User
from models.package import Package
from models.book import Booking
from models.hotels import Hotel

from datetime import date, datetime, timedelta

booking = Blueprint('bookingController', __name__)

@booking.route('/view')
def view():
    if not current_user.is_authenticated:
        flash("Please login or register first to get an account.", "danger")
        return redirect(url_for('auth.login'))
        
    if current_user.isAdmin:
        flash("Admin users cannot make bookings.", "danger")
        return redirect(url_for('packageController.packages'))
        
    form = BookForm()
    hotel_name=request.args.get('hotel_name').strip("'")
    the_package_to_be_booked = Package.getPackage(hotel_name=hotel_name)
    return render_template('booking.html', panel=hotel_name, form=form, package=the_package_to_be_booked)

@booking.route('/bookHotel', methods=['GET', 'POST'])
def bookHotel():
    if not current_user.is_authenticated:
        flash("Please login or register first to get an account.", "danger")
        return redirect(url_for('auth.login'))
        
    if current_user.isAdmin:
        flash("Admin users cannot make bookings.", "danger")
        return redirect(url_for('hotelController.hotels'))

    form = BookForm()
    hotel_name_raw = request.args.get('hotel_name') or request.form.get('hotel_name')
    
    if not hotel_name_raw:
        flash("Hotel not found.", "danger")
        return redirect(url_for('hotelController.hotels'))

    clean_name = hotel_name_raw.strip("'\"")
    import re
    safe_name = re.escape(clean_name)
    query = r'^"?\s*' + safe_name + r'\s*"?$'
    the_hotel_to_be_booked = Hotel.objects(hotel_name__iregex=query).first()

    if request.method == 'POST':
        check_in_date = request.form.get("check_in_date")
        check_out_date = request.form.get("check_out_date")
        holiday_type = request.form.get("holiday_type")

        if the_hotel_to_be_booked is not None:
            try:
                # TRY TO CREATE THE BOOKING
                Booking.createBooking(
                    check_in_date=check_in_date,
                    check_out_date=check_out_date, 
                    customer=current_user,
                    hotel=the_hotel_to_be_booked,
                    holiday_type=holiday_type
                )
                flash("Hotel successfully booked!", "success")
                return redirect(url_for('hotelController.hotels'))
                
            except ValidationError as e:
                # CATCH THE ERROR AND FLASH IT
                flash(str(e), "danger")
                return redirect(url_for('bookingController.bookHotel', hotel_name=clean_name))
        else:
            flash("Hotel not found in database.", "danger")
            return redirect(url_for('hotelController.hotels'))

    # If GET request, show the form
    return render_template('bookingHotel.html', panel=clean_name, form=form, hotel=the_hotel_to_be_booked)

@booking.route('/book', methods=['GET', 'POST'])
def book():
    if not current_user.is_authenticated:
        flash("Please login or register first to get an account.", "danger")
        return redirect(url_for('auth.login'))
        
    if current_user.isAdmin:
        flash("Admin users cannot make bookings.", "danger")
        return redirect(url_for('packageController.packages'))
 
    if request.method == 'POST':
        hotel_name=request.form.get("hotel_name")
        check_in_date=request.form.get("check_in_date")
        holiday_type = request.form.get("holiday_type")  # <-- THIS WAS MISSING

        existing_package = Package.getPackage(hotel_name=hotel_name)


        if existing_package is not None:
            aBooking = Booking.createBooking(
                check_in_date=check_in_date,  # This is the string from the form
                check_out_date=None,
                customer=current_user,
                package=existing_package,
                holiday_type=holiday_type
            ) 

            # Use Python's .replace() method here, not Jinja's |replace
            clean_title = existing_package.title.replace('"', '')

            # Use the string directly
            flash(f"Package Booking created for {current_user.name} at {clean_title} from {check_in_date} for {existing_package.duration} nights.", "success")

        return redirect(url_for('packageController.packages'))

@booking.route('/manageBookings')
@login_required
def manageBookings(days = -2000):
    bookings = list(Booking.getUserBookingsFromDate(customer=current_user, from_date=date.today()+timedelta(days = days)))
    if bookings:
        bookings.sort(key=lambda b: b.check_in_date)
    return render_template('userBookings.html', panel='Manage Bookings', bookings=bookings, now=datetime.now())


@booking.route("/updateBooking", methods=["POST"])
@login_required
def update():
    # 1. Fetch the correct form data
    package_title = request.form.get("package_title")
    hotel_name = request.form.get("hotel_name") # Added for hotels
    old_check_in_date = request.form.get("old_check_in_date")
    new_check_in_date = request.form.get("check_in_date")
    new_check_out_date = request.form.get("check_out_date") # Added for hotels

    try:
        # 2. Call the model and get the result
        updated_booking = Booking.updateBooking(
            old_check_in_date, 
            new_check_in_date, 
            current_user, 
            package_title=package_title,
            hotel_name=hotel_name,
            new_check_out_date=new_check_out_date
        )

        # 3. Validate before flashing
        if updated_booking:
          # RE-GENERATE ITINERARY BECAUSE DATES CHANGED
          updated_booking.itinerary = [] # Clear old one
          updated_booking.save()
          updated_booking.getItinerary() # <-- Call the correct method name
          flash("Booking has been successfully updated.", "success")
        else:
          flash("Booking not found or is in the past.", "danger")

    except ValidationError as e:
        # Catch date validation errors and flash them
        flash(str(e), "danger")

    return redirect(url_for('bookingController.manageBookings'))


@booking.route("/deleteBooking", methods=["POST"])
@login_required
def delete():
    package_title = request.form.get("package_title")
    hotel_name = request.form.get("hotel_name") # <-- Get hotel_name too
    check_in_date = request.form.get("old_check_in_date")

    # Use package_title OR hotel_name to find the exact booking
    the_booking = Booking.getBooking(check_in_date, current_user, package_title=package_title, hotel_name=hotel_name)
    
    if the_booking:
        the_booking.delete()
        flash("Booking has been successfully deleted.", "success")
        
    return redirect(url_for('bookingController.manageBookings'))

@booking.route('/getItinerary/<booking_id>')
@login_required
def getItinerary(booking_id):
    the_booking = Booking.objects(id=booking_id).first()
    
    if not the_booking or the_booking.customer.id != current_user.id:
        return jsonify({"error": "Booking not found"}), 404

    # If the booking doesn't have an itinerary saved yet, generate it once
    if not the_booking.itinerary:
        the_booking.getItinerary()

    # Return the saved itinerary
    return jsonify(the_booking.itinerary)