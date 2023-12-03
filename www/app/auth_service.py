from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from flask import flash
from .models import User
from . import db
from sqlalchemy.exc import IntegrityError

# Constants for hash method and flash message contents
HASH_TYPE = 'pbkdf2:sha256'
SUCCESS = 'success'
ERROR = 'error'
PASSWORD_MISMATCH = 'Passwords do not match.'
PASSWORD_LENGTH = 'Password must be at least 7 characters.'
LOGIN_SUCCESS = 'Signed in successfully!'
ACCOUNT_CREATED = "Account created! We've signed you in."
ACCOUNT_EXISTS = 'An account with this email already exists.'


def generate_hash(password):
    """
    Generates a password hash using a specified hashing algorithm.

    Parameters:
    password (str): The password to be hashed.

    Returns:
    str: The generated password hash.
    """
    return generate_password_hash(password, method=HASH_TYPE)


def validate_password(password1, password2):
    """
    Validates that two given passwords match and meet the length requirement.

    Parameters:
    password1 (str): The first password.
    password2 (str): The second password to compare with the first.

    Returns:
    bool: True if validation passes, False otherwise. Also flashes a message on failure.
    """
    if password1 != password2:
        flash(PASSWORD_MISMATCH, ERROR)
        return False
    if len(password1) < 7:
        flash(PASSWORD_LENGTH, ERROR)
        return False
    return True


def authenticate_and_login(email, password):
    """
    Authenticates a user based on email and password. Logs the user in on successful authentication.

    Parameters:
    email (str): The email of the user.
    password (str): The password of the user.

    Returns:
    bool: True if the user is authenticated and logged in, False otherwise.
    """
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user, remember=True)
        flash(LOGIN_SUCCESS, SUCCESS)
        return True
    else:
        return False


def create_user(email, first_name, password):
    """
    Creates a new user and adds them to the database.

    Parameters:
    email (str): The email of the new user.
    first_name (str): The first name of the new user.
    password (str): The password of the new user.

    Returns:
    User: The newly created user object.
    """
    hashed_password = generate_hash(password)
    new_user = User(email=email, first_name=first_name,
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def register_and_login(email, first_name, password1, password2):
    """
    Handles user registration and logs in the new user upon successful registration.

    Parameters:
    email (str): The email of the new user.
    first_name (str): The first name of the new user.
    password1 (str): The password of the new user.
    password2 (str): The password confirmation.

    Returns:
    bool: True if the user is successfully registered and logged in, False otherwise.
    """
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
