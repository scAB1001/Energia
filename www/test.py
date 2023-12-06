import os, unittest, json, re
from unittest.mock import patch
from flask import Flask, session
from app import app, db
from flask_login import login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from app.forms import LoginForm, RegistrationForm
from app.models import User, Car, UserInteraction
from app.auth_service import generate_hash, validate_password, valid_inputs, authenticate_and_login, create_user, register_and_login
from app.views import home, explore, saved, single_view, settings, delete_account

# C:\Users\AB\OneDrive\Documents\CODE\py\www
basedir = os.path.abspath(os.path.dirname(__file__))


class BasicTestCase(unittest.TestCase):
    
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'app.db')

        self.app = app.test_client()

        with app.app_context():
            db.create_all()

            if os.path.exists(os.path.join(basedir, 'app.db')):
                print("\tTest database created successfully.")

            self._create_test_data()

    def _create_test_data(self):
        # Creating valid test user, car and user-interaction 
        #   for authentication and interaction tests

        # Create users
        user1 = User(
            email='user1@example.com', first_name='User1',
            password=generate_hash('password1'))

        user2 = User(
            email='user2@example.com', first_name='User2',
            password=generate_hash('password2'))

        # Create cars
        car1 = Car(
            image='ferrariF512TR3', car_name='Ferrari F512 TR', make='Ferrari',
            model='F512 TR', year=1991, body_type='2-door berlinetta', horsepower=422,
            monthly_payment=3245.32, mileage=198978, like_count=11)
        
        car2 = Car(
            image='astonMartinSILagonda1', car_name='Aston Martin Lagonda Series 1', 
            make='Aston Martin', model='Lagonda', year=1974, body_type='4-door saloon', 
            horsepower=280, monthly_payment=4611.96, mileage=18324, like_count=14)
        
        car3 = Car(
            image='countachLP400Lamborghini1', car_name='Lamborghini Countach LP400', 
            make='Lamborghini', model='LP400', year=1974, body_type='2-door coupe', 
            horsepower=375, monthly_payment=8042.47, mileage=167228, like_count=86)
                
        db.session.add_all([user1, user2, car1, car2, car3])
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("\tTest data already exists in database.")
            return

        # User interactions
        #   User 1 likes Car 1 & 2, dislikes Car 3
        #   User 2 has not interacted with any cars
        interaction1 = UserInteraction(
            user_id=user1.id, car_id=car1.id, swiped_right=True)
        interaction2 = UserInteraction(
            user_id=user1.id, car_id=car2.id, swiped_right=True)
        interaction3 = UserInteraction(
            user_id=user1.id, car_id=car3.id, swiped_right=False)

        db.session.add_all([interaction1, interaction2, interaction3])
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("\tTest data already exists in database.")
            return

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    """
    # Model Basic Tests
    def test_valid_car_creation(self):
        with app.app_context():
            car1_id = db.session.get(Car, 1).id
            self.assertIsNotNone(car1_id)


    def test_invalid_car_creation(self):
        with app.app_context():
            car = Car(make='', model='', year=1900, like_count=0)
            db.session.add(car)

            with self.assertRaises(Exception):
                db.session.commit()
            
            self.assertIsNone(car.id)


    def test_valid_user_creation(self):
        with app.app_context():
            user1_id = db.session.get(User, 1).id
            self.assertIsNotNone(user1_id)

  
    def test_invalid_user_creation(self):
        with app.app_context():
            user_id = User(email='', first_name='', password='').id
            self.assertIsNone(user_id)


    def test_valid_user_interaction_creation(self):
        with app.app_context():
            interaction1_id = db.session.get(UserInteraction, 1).id
            self.assertIsNotNone(interaction1_id)


    def test_invalid_user_interaction_creation(self):
        with app.app_context():
            interaction = UserInteraction(
                user_id=1, car_id=3, swiped_right=None)
            db.session.add(interaction)

            with self.assertRaises(Exception):
                db.session.commit()
            
            self.assertIsNone(interaction.id)

    
    # Model Relationship Tests
    def test_valid_user_interaction_relationship(self):
        with app.app_context():
            # Retrieve user 1 from the database
            user1 = User.query.first()
            self.assertIsNotNone(user1, "Test user not found in database")

            # Retrieve car 1 from the database
            car1 = Car.query.first()
            self.assertIsNotNone(car1, "Test car not found in database")

            # Retrieve interaction 1 from the database
            test_interaction = UserInteraction.query.first()
            self.assertIsNotNone(test_interaction, "Test interaction not found in database")

            # Test the user 1 interaction relationship
            self.assertEqual(test_interaction.user, user1)

    
    def test_invalid_user_interaction_relationship(self):
        with app.app_context():
            # Retrieve user 2 from the database
            user2 = db.session.get(User, 2)
            self.assertIsNotNone(user2, "User 2 not found in database")

            # Retrieve car 1 from the database
            car1 = db.session.get(Car, 1)
            self.assertIsNotNone(car1, "Car 1 not found in database")

            # Retrieve all interactions from the database
            interactions = UserInteraction.query.all()
            self.assertIsNotNone(interactions, "No interactions found in database")

            # Test the user interaction relationship
            # This should fail because user 2 and none of the cars are related
            # because user 2 has not interacted with any cars.
            for interaction in interactions:
                self.assertNotEqual(interaction.user, user2)
    
"""    
    def test_login_form_validation(self):
        with app.app_context():
            # Base valid data
            base_data = {'email': 'user@example.com', 'password': 'ValidPass123'}

            # Test valid input
            form = LoginForm(data=base_data)
            self.assertTrue(form.validate())

            # Test invalid email
            invalid_email_data = base_data.copy()
            invalid_email_data['email'] = 'invalid-email'
            form = LoginForm(data=invalid_email_data)
            self.assertFalse(form.validate())

            # Test invalid (empty) password
            empty_pwd_data = base_data.copy()
            empty_pwd_data['password'] = ''
            form = LoginForm(data=empty_pwd_data)
            self.assertFalse(form.validate())


    def test_registration_form_validation(self):
        with app.app_context():
            # Base valid data
            base_data = {
                'email': 'newUser@example.com',
                'first_name': 'NewUser',
                'password': 'ValidPass123',
                'confirm_password': 'ValidPass123'
            }

            # Test valid input
            form = RegistrationForm(data=base_data)
            self.assertTrue(form.validate())

            # Test invalid (mismatch) password 1
            mismatch_pwd_data = base_data.copy()
            mismatch_pwd_data['confirm_password'] = 'DifferentPass123'
            form = RegistrationForm(data=mismatch_pwd_data)
            self.assertFalse(form.validate())

            # Test invalid (too long) password 2
            overflow_pwd_data = base_data.copy()
            overflow_pwd_data['password'] = f"{'.' * 19}"
            form = RegistrationForm(data=overflow_pwd_data)
            self.assertFalse(form.validate())

            # Test invalid (missing num/chars) password 3
            weak_pwd_data = base_data.copy()
            weak_pwd_data['password'] = 'weakpassword'
            form = RegistrationForm(data=weak_pwd_data)
            self.assertFalse(form.validate())

            # Test invalid first name (contains numbers) 1
            num_first_name_data = base_data.copy()
            num_first_name_data['first_name'] = 'NewUser1'
            form = RegistrationForm(data=num_first_name_data)
            self.assertFalse(form.validate())

            # Test invalid first name (empty) 2
            empty_first_name_data = base_data.copy()
            empty_first_name_data['first_name'] = ''
            form = RegistrationForm(data=empty_first_name_data)
            self.assertFalse(form.validate())
"""

    def test_like_count_increment(self):
        with app.app_context():
            # Retrieve the test car from the database (entry 1)
            car1 = Car.query.first()
            self.assertIsNotNone(car1, "Car 1 not found in database")

            # Save the car ID and like count for the test
            car1_id = car1.id
            before_increment = car1.like_count

            # Simulate the AJAX call to increment like count
            response = self.app.post(f'/toggle_count/{car1_id}', json={'liked': True})
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['like_count'], before_increment + 1)

            # Re-query the car to get the updated like count
            car1 = db.session.get(Car, 1)
            self.assertEqual(car1.like_count, before_increment + 1)

    def test_like_count_decrement(self):
        with app.app_context():
            # Retrieve the test car from the database
            car1 = Car.query.first()
            self.assertIsNotNone(car1, "Car 1 not found in database")

            # Save the car ID and like count for the test
            car1_id = car1.id
            before_decrement = car1.like_count

            # Simulate the AJAX call to increment like count
            response = self.app.post(
                f'/toggle_count/{car1_id}', json={'liked': False})
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['like_count'], before_decrement - 1)

            # Re-query the car to get the updated like count
            car1 = db.session.get(Car, 1)
            self.assertEqual(car1.like_count, before_decrement - 1)


    ###########################
    def test_home_page_loads(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)


    def test_404_page(self):
        response = self.app.get(
            '/this-route-does-not-exist', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
    
    
    # Authentication Tests
    def test_successful_login(self):
        with app.app_context():
            response = self.app.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpassword'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(current_user.is_authenticated)


    def test_unsuccessful_login(self):
        with app.app_context():
            response = self.app.post('/login', data={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)


    def test_valid_user_registration(self):
        with app.app_context():
            response = self.app.post('/signup', data={
                'email': 'new@example.com',
                'first_name': 'New',
                'password': 'newpassword',
                'confirm_password': 'newpassword'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(current_user.is_authenticated)


    def test_invalid_user_registration(self):
        with app.app_context():
            # Test registration with invalid data
            response = self.app.post('/register', data={
                'username': 'us',  # Assuming this is too short
                'email': 'newuser@example.com',
                'password': 'newpassword',
                'confirm': 'newpassword'
            }, follow_redirects=True)
            self.assertIn(b'Registration failed', response.data)


    def test_logout(self):
        with app.app_context():
            # First login the user
            self.test_successful_login()
            response = self.app.get('/logout', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertFalse(current_user.is_authenticated)


    # View Functionality Tests
    def test_like_car(self):
        with app.app_context():
            self.test_successful_login()  # Ensure the user is logged in
            response = self.app.post(
                '/toggle_count/1', json={'liked': True}, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['like_count'], 1)
"""


if __name__ == '__main__':
    unittest.main()

