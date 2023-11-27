from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from .auth_service import authenticate_user, create_user, migrate_password
from .forms import LoginForm, RegistrationForm
from sqlalchemy.exc import IntegrityError

auth = Blueprint('auth', __name__)
DANGER, SUCCESS = 'error', 'success'
MAX_LOGIN_ATTEMPTS = 3


# Helper method to handle user login
def handle_login(email, password):
    user = authenticate_user(email, password)
    if user:
        migrate_password(user, password)  # Migrate password if needed
        login_user(user, remember=True)
        flash(f'Logged in successfully!', category=SUCCESS)
        return True
    else:
        flash('Incorrect email or password, try again.', category=DANGER)
        return False


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # Check if max attempts reached and redirect to signup if so
    if session.get('login_attempts', 0) >= MAX_LOGIN_ATTEMPTS:
        flash('Maximum login attempts reached. Please sign up.', category=DANGER)
        return redirect(url_for('auth.signup'))

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        if handle_login(email, password):
            # Reset login attempts on successful login
            session['login_attempts'] = 0
            return redirect(url_for('views.home'))
        else:
            # Increment the login attempt count
            session['login_attempts'] = session.get('login_attempts', 0) + 1
            remaining_attempts = MAX_LOGIN_ATTEMPTS - session['login_attempts']
            flash(f'You have {remaining_attempts+1} attempts remaining.', category=DANGER)

    return render_template("/admin/login.html", form=form, user=current_user, title='Login')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session['login_attempts'] = 0
    flash(f'Logged out successfully!', category=SUCCESS)

    return redirect(url_for('views.home'))


# Helper method to handle user registration
def handle_registration(email, first_name, password1, password2):
    if password1 != password2:
        flash('Passwords do not match.', category=DANGER)
        return False
    elif len(password1) < 7:
        flash('Password must be at least 7 characters.', category=DANGER)
        return False
    else:
        try:
            user = create_user(email, first_name, password1)
        except IntegrityError:
            db.session.rollback()
            flash('An account with this email already exists.', category=DANGER)
            return False
        if user:
            login_user(user, remember=True)
            flash('Account created!', category=SUCCESS)
            return True
        else:
            flash('Unable to create an account at this time. Try again.', category=DANGER)
            return False


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if not current_user.is_authenticated and session.get('login_attempts', 0) >= MAX_LOGIN_ATTEMPTS: ##
        flash(f'Too many login attempts, create a new account.', category=DANGER)

    # If user is already logged in and wants to create another account,
    #   they will be logged out of the initial upon creation
    if current_user.is_authenticated:
        logout()

    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        first_name = form.first_name.data
        password1 = form.password.data
        password2 = form.confirm_password.data

        if handle_registration(email, first_name, password1, password2):
            # Reset login attempts on successful sign-up and login
            session['login_attempts'] = 0
            return redirect(url_for('views.home'))
        else:
            flash('Unable to create an account at this time. Try again.', category=DANGER)

    return render_template("/admin/signup.html", form=form, user=current_user, title='Signup')
