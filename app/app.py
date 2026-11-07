# https://medium.com/@dmitryrastorguev/basic-user-authentication-login-for-flask-using-mongoengine-and-wtforms-922e64ef87fe

from flask_login import login_required, current_user
from flask import Blueprint, render_template, request, jsonify, url_for, redirect
from __init__ import app, db #, login_manager

from werkzeug.security import generate_password_hash

# Register Blueprint so we can factor routes
# from bmi import bmi, get_dict_from_csv, insert_reading_data_into_database

from controllers.dashboard import dashboard
from controllers.auth import auth
from controllers.bookController import booking
from controllers.packageController import package
from controllers.attractionController import attraction
from controllers.hotelController import hotel



from models.package import Package
from models.book import Booking
from models.users import User
from models.attractions import Attraction
from models.hotels import Hotel
from models.forms import BookForm

#for uploading file
import csv
import io
import json
import datetime as dt
import os

# register blueprint from respective module
app.register_blueprint(dashboard)
app.register_blueprint(auth)
app.register_blueprint(booking)
app.register_blueprint(package)
app.register_blueprint(attraction)
app.register_blueprint(hotel)

@app.template_filter('formatdate') # use this name
def format_date(value, format="%#d/%m/%Y"):
    """Format a date time to (Default): dd/mm/YYYY"""
    if value is None:
        return ""
    return value.strftime(format)

@app.template_filter('formatmoney') # use this name
def format_money(value, ndigits=2):
    """Format money with 2 decimal digits"""
    if value is None:
        return ""
    return f'{value:.{ndigits}f}'

@app.route('/')
def home():
    return render_template('home.html', panel='home')


@app.route('/base')
def show_base():
    return render_template('base.html')

@app.route("/upload", methods=['GET','POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template("upload.html", name=current_user.name, panel="Upload")
    elif request.method == 'POST':
        type = request.form.get('type')
        if type == 'create':
            print("No create Action yet")
        elif type == 'upload':
            file = request.files.get('file')
            datatype = request.form.get('datatype')

            data = file.read().decode('utf-8')
            dict_reader = csv.DictReader(io.StringIO(data), delimiter=',', quotechar='"')
            file.close()

            if datatype == "Users":
              for item in list(dict_reader):
                pwd = generate_password_hash(item['password'], method='sha256')
                is_admin = True if str(item.get('isAdmin', 'False')).strip().lower() in ['true', '1', 'yes'] else False
                User.createUser(email=item['email'], password=pwd, name=item['name'], isAdmin=is_admin)
            elif datatype == "Attractions":
              for item in list(dict_reader):
                  time_slots_raw = item.get('time_slot', '[]')
                  if isinstance(time_slots_raw, str):
                      import ast
                      try:
                          time_slots = ast.literal_eval(time_slots_raw)
                      except:
                          time_slots = []
                  else:
                      time_slots = []

                  is_free = True if str(item.get('is_free', 'False')).strip().lower() in ['true', '1', 'yes'] else False
                  Attraction(
                      name=item['name'],
                      category=item.get('category'),
                      time_slot=time_slots,
                      neighborhood=item.get('neighborhood'),
                      is_free=is_free,
                      cost_range=item.get('cost_range'),
                      michelin_award=item.get('michelin_award') if item.get('michelin_award') else None,
                      signature_dish=item.get('signature_dish') if item.get('signature_dish') else None,
                      opening_time=item.get('opening_time'),
                      closing_time=item.get('closing_time'),
                      details=item.get('details'),
                      address=item.get('address'),
                      image_url=item.get('image_url')
                  ).save()
            elif datatype == "Hotels":
                for item in list(dict_reader):
                    # Clean and parse amenities if stored as string/list representation
                    amenities_raw = item.get('amenities', '[]')
                    if isinstance(amenities_raw, str):
                        import ast
                        try:
                            amenities = ast.literal_eval(amenities_raw)
                        except:
                            amenities = []
                    else:
                        amenities = []
                    
                    Hotel.createHotel(
                        hotel_name=item['hotel_name'],
                        neighborhood=item['neighborhood'],
                        hotel_class=item['hotel_class'],
                        est_nightly_price=float(item['estimated_nightly_price'].replace('$', '').strip()),
                        description=item['description'],
                        address=item['address'],
                        amenities=amenities,
                        image_url=item['image_url']
                    )
            elif datatype == "Package":
                for item in list(dict_reader):
                    Package.createPackage(hotel_name=item['hotel_name'], duration=int(item['duration']),
                        unit_cost=float(item['unit_cost']), image_url=item['image_url'],
                        description=item['description'])
            elif datatype == "Booking":
                for item in list(dict_reader):
                    existing_user = User.getUser(email=item['customer'])
                    existing_package = Package.getPackage(hotel_name=item['hotel_name'])
                    check_in_date=dt.datetime.strptime(item['check_in_date'], "%Y-%m-%d")

                    aBooking = Booking.createBooking(check_in_date=check_in_date, customer=existing_user, package=existing_package)
                    aBooking.calculate_total_cost()
                    
        return render_template("upload.html", panel="Upload")
    
@app.route("/changeAvatar")
def changeAvatar():
    basedir = os.path.abspath(os.path.dirname(__file__))
    # Specify the relative path to the subfolder
    subfolder_path = os.path.join('assets', 'img/avatar')
    # Join the base directory with the subfolder path
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    files = []
    for filename in os.listdir(subfolder_abs_path):
        path = os.path.join(subfolder_abs_path, filename)
        if os.path.isfile(path):
            files.append(filename)
            # url_for('static') /static/default.jpg etc
    return render_template("changeAvatar.html", filenames=files, panel="Change Avatar") 

@app.route("/chooseAvatar", methods=['POST'])
def chooseAvatar():
    # get the filename
    chosenPath = request.json['path']
    print('chosen path: ', chosenPath)
  
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Specify the relative path to the subfolder
    subfolder_path = os.path.join('assets', 'img/avatar')

    # Join the base directory with the subfolder path
    subfolder_abs_path = os.path.join(basedir, subfolder_path)
    
    filename = chosenPath.split('/')[-1]
    User.addAvatar(current_user, filename)
    
    return jsonify(path=chosenPath)

  