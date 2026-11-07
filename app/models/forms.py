from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField, StringField, PasswordField, validators, DateTimeField, FloatField
from wtforms.validators import Email, Length, InputRequired

class RegForm(FlaskForm):
    email = StringField('Email',  validators=[InputRequired(), Email(message='Invalid email'), Length(max=30)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=5, max=20)])
    name = StringField('Name')

class BookForm(FlaskForm):
    check_in_date = DateTimeField('check_in_date', format='%Y-%m-%d', validators=[validators.InputRequired()])
    check_out_date = DateTimeField('check_out_date', format='%Y-%m-%d', validators=[validators.InputRequired()]) # <-- Add this
    holiday_type = SelectField('holiday_type', choices=[('Food', 'Food'), ('Family', 'Family'), ('Nature', 'Nature')], validators=[validators.InputRequired()])
