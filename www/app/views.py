from app.models import UserInteraction
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, session
from flask_login import login_required, logout_user, current_user
from .models import User, Car, Lease, UserInteraction
from .forms import LoginForm, RegistrationForm
from app import app, db, admin
from flask_admin.contrib.sqla import ModelView

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Car, db.session))
admin.add_view(ModelView(Lease, db.session))
admin.add_view(ModelView(UserInteraction, db.session))

import json
from collections import Counter
from datetime import datetime

# Flash message flags
DANGER, SUCCESS = 'danger', 'success'
views = Blueprint('views', __name__)


# General
"""  

    Helper variables and methods

"""

click_count = 30
should_increment = True
@views.route('/toggle_count', methods=['POST'])
def toggle_count():
    global click_count, should_increment
    if should_increment:
        click_count += 1
    else:
        click_count -= 1
    # Toggle the state
    should_increment = not should_increment
    #print(f"Current click count: {click_count}")
    return jsonify(click_count=click_count)


# Attempts to stage and apply a commit to the db, else rollback the attempt
def update_db(entry):
    try:
        db.session.add(entry)
        db.session.commit()
    except Exception:
        db.session.rollback()
        flash(f"An error occurred while adding this entry.", DANGER)


def is_table_empty(model):
    # Returns True if the table is empty, False otherwise
    print(f"{model.__name__} count: {db.session.query(model).count()}")
    return db.session.query(model).count() == 0


def clear_tables():
    # Clear all data from tables
    if not is_table_empty(UserInteraction):
        UserInteraction.query.delete()
        
    if not is_table_empty(Lease):
        Lease.query.delete()
    
    if not is_table_empty(Car):
        Car.query.delete()
    
    if not is_table_empty(User):
        User.query.delete()
    
    db.session.commit()
    

# DANGER #
# Do not use until password is hashed
def pre_populate_db():
    # Clear all tables
    #clear_tables()
    
    # Create Users
    if is_table_empty(User) and is_table_empty(Car) and is_table_empty(Lease) and is_table_empty(UserInteraction):
        users = [
            User(email='user1@example.com', password='password1', first_name='User1'),
            User(email='user2@example.com', password='password2', first_name='User2'),
            User(email='user3@example.com', password='password3', first_name='User3'),
            User(email='user4@example.com', password='password4', first_name='User4'),
            User(email='user5@example.com', password='password5', first_name='User5'),
        ]

        # Create Cars
        cars = [
            Car(model='Model S', make='Tesla', 
                year=2020, body_type='Sedan', monthly_payment=700.00, horsepower=670),

            Car(model='Mustang', make='Ford', 
                year=2019, body_type='Coupe', monthly_payment=500.00, horsepower=450)

            # Add more cars as needed
        ]

        # Add users and cars to the session
        db.session.add_all(users)
        db.session.add_all(cars)

        # Commit the users and cars to the database
        db.session.commit()

        # Create Leases and User Interactions
        for user in users:
            for car in cars:
                lease = Lease(user_id=user.id, car_id=car.id, term_length=36, mileage_limit=12000)
                interaction = UserInteraction(user_id=user.id, car_id=car.id, swipe_type='like', timestamp=datetime.now())
                db.session.add(lease)
                db.session.add(interaction)

        # Commit the leases and interactions to the database
        db.session.commit()


def display_user_data():
    users = User.query.all()
    for user in users:
        print(f"User: {user.first_name}, Email: {user.email}")

        # Print all leases for this user
        for lease in user.leases:
            print(
                f"\tLeased Car ID: {lease.car_id}, Term: {lease.term_length} months")

        # Print all interactions for this user
        for interaction in user.interactions:
            print(
                f"\tInteraction: {interaction.swipe_type} with Car ID: {interaction.car_id}")


def display_table_nicely(numCards, li):
    print(f'\nList of {numCards} cars:\n[')
    for card in li:
        print('\t{')
        data = card.items()
        for key, value in data:
            if isinstance(value, str):
                value = value.replace('\n', ' ').replace('\t\t', ', ')
            print(f'\t\t{key}: {value},')
        print('\t},')
    print(']\n')


def delete_user_interactions(user_id):
    """
    Deletes all UserInteraction entries associated with a specific user.

    :param user_id: ID of the user whose interactions should be deleted.
    """
    try:
        # Query UserInteraction entries for the specific user
        to_delete = UserInteraction.query.filter_by(
            user_id=user_id)

        # Check if there are interactions to delete
        if to_delete.count() > 0:
            to_delete.delete()
            db.session.commit()
            print(f"All interactions for user ID {user_id} have been deleted.")
        else:
            print(f"No interactions found for user ID {user_id}.")

    except Exception as e:
        db.session.rollback()
        print(
            f"An error occurred while deleting interactions for user ID {user_id}: {e}")


def pre_populate_tblCars():
    # Reset cars abd user interactions tables when meeting the explore page?
    if not is_table_empty(Car):
        Car.query.delete()
        print(f"Deleting rows... table_empty: {is_table_empty(Car)}\n")
        
    if current_user.is_authenticated:
        delete_user_interactions(current_user.id)
        db.session.commit()
        print(f"Deleting rows... table_empty: {is_table_empty(UserInteraction)}")
        
    
    try:
        # Format: Car(car_name, make, model, year, body_type, horsepower, monthly_payment, mileage)
        cars_to_add = [
            Car(image='astonMartinSILagonda1', car_name='Aston Martin Lagonda Series 1', make='Aston Martin', model='Lagonda',
            year=1974, body_type='4-door saloon', horsepower=280, monthly_payment=54611.96, mileage=18324),
        
            Car(image='astonMartinSIILagonda2', car_name='Aston Martin Lagonda Series 2', make='Aston Martin', model='Lagonda', 
                year=1976, body_type='4-door saloon', horsepower=280, monthly_payment=15461.56, mileage=103633),
                
            Car(image='astonMartinSIIILagonda3', car_name='Aston Martin Lagonda Series 3', make='Aston Martin', model='Lagonda', 
                year=1986, body_type='4-door saloon', horsepower=0, monthly_payment=7766.58, mileage=132084),

            Car(image='astonMartinSIVLagonda4', car_name='Aston Martin Lagonda Series 4', make='Aston Martin', model='Lagonda', 
                year=1987, body_type='4-door saloon', horsepower=0, monthly_payment=33633.98, mileage=123117),

            Car(image='ferrariTestarossa1', car_name='Ferrari Testarossa', make='Ferrari', model='Testarossa', 
                year=1984, body_type='2-door berlinetta', horsepower=385, monthly_payment=34185.91, mileage=146545),

            Car(image='ferrariF512M2', car_name='Ferrari F512 M', make='Ferrari', model='F512 M', 
                year=1994, body_type='2-door berlinetta', horsepower=434, monthly_payment=6352.03, mileage=196267),
            
            Car(image='ferrariF512TR3', car_name='Ferrari F512 TR', make='Ferrari', model='512 TR', 
                year=1991, body_type='2-door berlinetta', horsepower=422, monthly_payment=31245.32, mileage=198978),

            Car(image='ferrari308GTRainbow4', car_name='Ferrari 308 GT Bertone Rainbow', make='Ferrari', model='308 GT', 
                year=1976, body_type='2-door coupe', horsepower=255, monthly_payment=52585.91, mileage=89017),
            
            Car(image='countachLP400Lamborghini1', car_name='Lamborghini Countach LP400', make='Lamborghini', model='LP400', 
                year=1974, body_type='2-door coupe', horsepower=375, monthly_payment=82042.47, mileage=167228),
            
            Car(image='countachLP500Lamborghini2', car_name='Lamborghini Countach LP500', make='Lamborghini', model='LP500', 
                year=1982, body_type='2-door coupe', horsepower=370, monthly_payment=27854.73, mileage=100220),

            Car(image='countachLP5000LamborghiniQuattrovalvole3', car_name='Lamborghini Countach LP5000 Quattrovalvole', make='Lamborghini', model='LP5000 Quattrovalvole', 
                year=1985, body_type='2-door coupe', horsepower=455, monthly_payment=81930.27, mileage=103074),

            Car(image='countach25thAnniversaryLamborghini4', car_name='Lamborghini Countach 25th Anniversary', make='Lamborghini', model='25th Anniversary Edition', 
                year=1988, body_type='2-door coupe', horsepower=414, monthly_payment=36409.78, mileage=140320),
            
            Car(image='mercedesBenz300SLGullwing1', car_name='Mercedes-Benz 300SL Gullwing', make='Mercedes-Benz', model='300SL', 
                year=1954, body_type='2-door coupe', horsepower=215, monthly_payment=22230.65, mileage=92350)
        ]
        
        # Add cars to the database
        print("\nAdding rows...")
        db.session.add_all(cars_to_add)
        db.session.commit()
        is_table_empty(Car)    
        return jsonify({"status": "success", "message": "Cars added successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500



# Routes
"""
    
    View entries

"""
@views.route('/')
def home():
    #clear_tables()
    
    # DANGER #
    #if not User.query.first():
    #    pre_populate_db()


    return render_template('/site/home.html', title='Home', user=current_user)


@app.route('/react', methods=['POST'])
@login_required
def react():
    data = request.json#; print(f"Payload data:\n{data}")
    
    try:
        # .get() results in None type if not found
        carID = int(data.get('carID'))
        status = data.get('liked') == True
        
    except (TypeError, ValueError):
        return jsonify({"status": "error", "message": "Invalid data"}), 400
    
    # Create a new user interaction entry
    new_interaction = UserInteraction(
        user_id=current_user.id, 
        car_id=carID, 
        swiped_right=status
    )
    db.session.add(new_interaction)
    
    try:
        db.session.commit()
        return jsonify({"status": "success", "carID": carID, "liked": status})
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

    

@views.route('/test')
def test():
    #if not is_table_empty(UserInteraction):
    #    interactions = UserInteraction.query.all()
    #    for interaction in interactions:
    #        print(f"UserID: {interaction.user_id}, CarID: {interaction.car_id}, Liked: {interaction.swiped_right}")
    #else:
    #    print("UserInteraction table EMPTY")    
    
    #tblCars = Car.query.all()
    #car_card_details = []
    #for car in tblCars:
    #    car_card_details.append(car.card_info())

    #numCards = len(car_card_details)
    ##display_table_nicely(numCards, car_card_details)
    
    #return render_template(
    #    'test.html', title='Test', user=current_user, 
    #    cars=car_card_details, numCards=numCards)
    
    
    car = Car.query.first().full_details()
    display_table_nicely(1, [car])
    
    return render_template('test.html', title='Test', user=current_user, car=car)
    


@views.route('/explore')
@login_required
def explore():
    pre_populate_tblCars()
    numCards = db.session.query(Car).count()
    tblCars = Car.query.all()
    
    cars = []
    for car in tblCars:
        cars.append(car.card_info())
        
    return render_template('/site/explore.html', title='Explore', user=current_user, cars=cars, numCards=numCards)


@views.route('/saved')
@login_required
def saved():
    return render_template('/site/saved.html', title='Saved', user=current_user)


@views.route('/saved/single_view')
@login_required
def single_view():
    #tblCars = Car.query.first()  # all()
    
    # Query car by ID and Name (Only one car at a time)
    cars = [Car.query.first().card_info()]
    #for car in tblCars:
    #    cars.append(car.card_info())
    
    return render_template('/site/single_view.html', title='Car', user=current_user, cars=cars)
    


@views.route('/history')
@login_required
def history():
    return render_template('/site/history.html', title='History', user=current_user)


@views.route('/settings')
@login_required
def settings():
    states = UserInteraction.query.all()
    for i in states:
        print(i)
    return render_template('/site/settings.html', title='Settings', user=current_user)


@views.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    if current_user.is_authenticated:
        # Delete current user and current user_interaction
        user = User.query.get(current_user.id)
        delete_user_interactions(current_user.id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash('Your account has successfully been deleted.', category=SUCCESS)
        else:
            flash('User not found.', category=DANGER)
        # Logout
        logout_user()
        session['login_attempts'] = 0
        return redirect(url_for('auth.login'))
    else:
        flash('You must be logged in to perform this action.', category=DANGER)
        return redirect(url_for('auth.login'))
    return True


@app.errorhandler(404)
def not_found_error(error):
    return render_template('/error/404.html', title='Error: 404', user=current_user), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()  # Rollback the session in case of database errors
    return render_template('/error/500.html', title='Error: 500', user=current_user), 500
