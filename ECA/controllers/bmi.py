from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from datetime import datetime, date
from flask_login import current_user
from models.bmidaily import BMIDAILY
from models.bmilog import BMILOG
from models.users import User

bmi = Blueprint('bmi', __name__)

# This following functions is for GET /log, and POST /process via log.html and log.js

@bmi.route('/log')
def log():
    return render_template('log.html', name=current_user.name, panel="Logging BMI")

@bmi.route('/process',methods= ['POST'])
def process():
    weight  = float(request.form['weight'])
    height = float(request.form['height'])
    unit = request.form['unit']

    # In /log, the date of BMI log is assumed to be today
    today = date.today()
    now = datetime.now()

    try:

        # First store the bmilog, by default there the current user is already an user
        # So, if no user can be retrieved, then there is an exception

        existing_user = User.getUser(email=current_user.email)
        bmilogObject = BMILOG.createBMILOG(user=existing_user, datetime=now, weight=weight, height=height, unit=unit, bmi=0.0)
        bmilogObject.bmi = bmilogObject.computeBMI()
        bmilogObject.save()

        bmidaily = BMIDAILY.getBMIDAILY(user=existing_user, date=today) #GET INFO

        # Check whether there is existing bmidailylog for the user

        if bmidaily:

            # if Yes, update the avergeBMI
            new_bmi_average = bmidaily.updatedBMI(bmilogObject.bmi)
            bmidaily.numberOfMeasures += 1
            bmidaily.averageBMI = new_bmi_average
            bmidaily.save()

        else:

            # if No, initialize the averageBMI
            BMIDAILY.createBMIDAILY(existing_user, today, 1, bmilogObject.bmi)
            # bmidailyObject.save()

    except Exception as e:
        print(f"{e}")
        return jsonify({})

    return jsonify({'bmi' : bmilogObject.bmi})

# This following functions is for GET /log2 and POST /process via log2.html and log2.js

@bmi.route('/log2')
def log2():
    all_users = User.objects()
    return render_template('log2.html', name=current_user.name, panel="Logging BMI 2", user_list=all_users)

@bmi.route('/process2',methods= ['POST'])
def process2():

    # Get the parameters posted by form in log2.html
    weight  = float(request.form['weight'])
    height = float(request.form['height'])
    unit = request.form['unit']
    user_email = request.form['user_email']
    date = request.form['date']

    datetime_object = datetime.strptime(date, '%Y-%m-%dT%M:%S')
    date_object= datetime_object.date()

    try:

        # First store the bmilog, by default there the current user is already an user
        # So, if no user can be retrieved, then there is an exception
        existing_user = User.getUser(email=user_email)
        bmilogObject = BMILOG.createBMILOG(user=existing_user, datetime=datetime_object, weight=weight, height=height, unit=unit, bmi=0.0)
        bmilogObject.bmi = bmilogObject.computeBMI()
        bmilogObject.save()

        bmidaily = BMIDAILY.getBMIDAILY(user=existing_user, date=date_object) #GET INFO

        # Check whether there is existing bmidailylog for the user

        if bmidaily:

            # if Yes, update the avergeBMI
            new_bmi_average = bmidaily.updatedBMI(bmilogObject.bmi)
            bmidaily.numberOfMeasures += 1
            bmidaily.averageBMI = new_bmi_average
            bmidaily.save()

        else:

            # if No, initialize the averageBMI
            BMIDAILY.createBMIDAILY(existing_user, date_object, 1, bmilogObject.bmi)
            # bmidailyObject.save()

    except Exception as e:
        print(f"{e}")
        return jsonify({})

    return redirect(url_for('bmi.log2'))