from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from flask import flash
from .models import User
from . import db
from sqlalchemy.exc import IntegrityError

# Constants for messages and categories
SUCCESS = 'success'
ERROR = 'error'
PASSWORD_MISMATCH = 'Passwords do not match.'
PASSWORD_LENGTH = 'Password must be at least 7 characters.'
LOGIN_SUCCESS = 'Signed in successfully!'
ACCOUNT_CREATED = "Account created! We've signed you in."
ACCOUNT_EXISTS = 'An account with this email already exists.'

HASH_TYPE = 'pbkdf2:sha256'


def generate_hash(password):
    return generate_password_hash(password, method=HASH_TYPE)


def validate_password(password1, password2):
    if password1 != password2:
        flash(PASSWORD_MISMATCH, ERROR)
        return False
    if len(password1) < 7:
        flash(PASSWORD_LENGTH)
        return False
    return True


def authenticate_and_login(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user, remember=True)
        flash(LOGIN_SUCCESS, SUCCESS)
        return True
    else:
        return False


def create_user(email, first_name, password):
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, first_name=first_name,
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def register_and_login(email, first_name, password1, password2):
    if not validate_password(password1, password2):
        return False
    try:
        user = create_user(email, first_name, password1)
        login_user(user, remember=True)
        flash(ACCOUNT_CREATED, SUCCESS)
        return True
    except IntegrityError:
        db.session.rollback()
        flash(ACCOUNT_EXISTS, ERROR)
        return False
