from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models.attractions import Attraction

attraction = Blueprint('attractionController', __name__)

@attraction.route('/attractions')
def attractions():
    # Fetch all attractions from the database
    all_attractions = Attraction.objects()
    
    # Render the template
    return render_template('attractions.html', all_attractions=all_attractions)