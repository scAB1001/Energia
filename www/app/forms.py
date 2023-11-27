from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, StringField, FloatField, PasswordField, SubmitField
from wtforms.validators import DataRequired, NumberRange, Length, Email, EqualTo

STR_MESSAGE = "ERR: Enter a name between 2 and 20 characters long."
NUM_MESSAGE = "ERR: Enter a number must be between 0 and 1000000."

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
