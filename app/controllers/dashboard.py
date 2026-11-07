from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from models.book import Booking

dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/trend_chart', methods=['GET', 'POST'])
def trend_chart():
    if request.method == 'GET':
        # Render the new dashboard HTML template
        return render_template('dashboard.html', panel="Dashboard")
    
    elif request.method == 'POST':
        # Call the new model method to get all the dashboard data
        data = Booking.getDashboardData()
        
        # Return it as JSON
        return jsonify(data)