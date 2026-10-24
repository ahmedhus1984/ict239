from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta, date
from app import db

import csv
import io
from statistics import mean
import json

from models.bmidaily import BMIDAILY
# from models.chart import CHART

dashboard = Blueprint('dashboard', __name__)

def getChartDim(user_email=None):

    # meta = {'collection': 'bmidaily'}
    # user = db.ReferenceField(User)
    # date = db.DateTimeField()
    # numberOfMeasures = db.IntField()
    # averageBMI = db.FloatField()
    
    chartDim = {} 
    labels = []
    
    # New Output 
    # var chartDim = data.chartDim; 
    # {'usr_1': [[datetime1, 23], [datetime2, 21.5], ...], 'usr_2': [[],[], ... ],  ...}
    # var xLabels = data.labels;
    # [] 

    try:
        bmidailys = BMIDAILY.objects()
        chartDim = {}

        for bmidaily in bmidailys:
            
            if not user_email or (bmidaily.user.email == user_email): 
                bmis = chartDim.get(bmidaily.user.name)
                if not bmis:
                    chartDim[bmidaily.user.name]=[[bmidaily.date, bmidaily.averageBMI]]
                else:
                    bmis.append([bmidaily.date, bmidaily.averageBMI])
            
        # make sure the datetime line is sorted    
        for value in chartDim.values():
            value.sort(key=lambda x: x[0])
        
        return chartDim, labels

    except:

        return None

def getAveDict():
    
    # meta = {'collection': 'bmidaily'}
    # user = db.ReferenceField(User)
    # date = db.DateTimeField()
    # numberOfMeasures = db.IntField()
    # averageBMI = db.FloatField()
    
    aveDict = {} 
    
    # New Output - dictionary with user name as key and average BMI as value
    # aveDict
    # {'usr_1': 12.23, 'usr_2': 12.23,  ...}

    try:
        bmidailys = BMIDAILY.objects()
        for bmidaily in bmidailys:
            user_name, aveBMI = bmidaily.user.name, bmidaily.averageBMI
            aves = aveDict.get(user_name)
            if not aves:
                aveDict[user_name]=[aveBMI]
            else:
                aves.append(aveBMI)
        
        for key, values in aveDict.items():
            aveDict[key]=mean(values)
        
        return aveDict
    except:
        return None

# chart2 GET and POST act in tandum, POST done via myChart_CSV2.js

@dashboard.route('/chart2', methods=['GET', 'POST'])
def chart2():
    if request.method == 'GET':
        #I want to get some data from the service
        return render_template('bmi_chart2.html', name=current_user.name, email_id=current_user.email, panel="BMI Chart")    #do nothing but to show index.html
    elif request.method == 'POST':
        
        # Retrieve data from AJAX POST
        res = request.get_data("data")
        d_token = json.loads(res)
        email_id = d_token['email_id'] 
        
        # if it is admin, all BMIDAILY records are to be charted
        if email_id == "admin@abc.com":
            email_id = None
            
        chartDim, labels = getChartDim(user_email=email_id)
        
        return jsonify({'chartDim': chartDim, 'labels': labels})

# chart3 GET and POST act in tandum, POST done via myChart_CSV3.js

@dashboard.route('/chart3', methods=['GET', 'POST'])
def chart3():
    if request.method == 'GET':
        #I want to get some data from the service
        return render_template('bmi_chart3.html', name=current_user.name, panel="BMI Chart")    #do nothing but to show index.html
    
    elif request.method == 'POST':
    
        aveDict = getAveDict()
        return jsonify({'averages': aveDict})

# Only GET, /dashboard only produces the dashboard view 
   
@dashboard.route('/dashboard')
@login_required
def render_dashboard():
    return render_template('dashboard.html', name=current_user.name, panel="Dashboard")

# Only GET, /chart produces the BMI chart at the Frontend via myChart_CSV.js

@dashboard.route('/chart')
@login_required
def chart():
    return render_template('bmi_chart.html', name=current_user.name, panel="BMI Chart")
