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
            password=generate_hash('Password1'))

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

    
    def login_test_user(self):
        """# Implement the logic to log in a test user
        #   for authentication and interaction tests
        with app.app_context():
            user = db.session.get(User, 1)
            self.assertIsNotNone(user, "Test user not found in database")
        
        # Log in the user using session transaction
        with self.app.session_transaction() as session:
            session['user_id'] = user.id
            session['_fresh'] = True
            self.assertTrue(user.is_authenticated)"""
        with self.app as client:
            # Login the test user
            user_data = {'email': 'user1@example.com',
                              'password': 'Password1'}
            login_response = client.post('/login', data=user_data, follow_redirects=True)
        
            with app.app_context():
                user = db.session.get(User, 1)
                self.assertIsNotNone(user, "Test user not found in database")
                
                # Check if login was successful
                self.assertEqual(login_response.status_code, 200)
                self.assertIn('/', login_response.get_data(as_text=True))



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
    

    def test_delete_user(self):
        with app.app_context():
            # Confirm that 2 users exist to begin with
            users = User.query.all()
            user_count = len(users)
            self.assertEqual(user_count, 2)

            user2 = db.session.get(User, 2)
            self.assertIsNotNone(user2)
        
            db.session.delete(user2)
            db.session.commit()

            # Check if user 2 exists
            new_user2 = db.session.get(User, 2)
            self.assertIsNone(new_user2)

            # Double check if user 2 was deleted
            new_users = User.query.all()
            new_user_count = len(new_users)
            self.assertEqual(new_user_count, user_count - 1)

    
    def test_delete_user_interactions(self):
        with app.app_context():
            # Confirm that 3 interactions exist for user 1 to begin with
            interactions = UserInteraction.query.filter_by(user_id=1).all()
            interaction_count = len(interactions)
            self.assertEqual(interaction_count, 3)

            # Delete interaction 3 for user 1
            interaction3 = db.session.get(UserInteraction, 3)
            self.assertIsNotNone(interaction3)

            db.session.delete(interaction3)
            db.session.commit()

            # Check if interaction 3 exists
            new_interaction3 = db.session.get(UserInteraction, 3)
            self.assertIsNone(new_interaction3)

            # Double check if interaction 3 was deleted
            new_interactions = UserInteraction.query.filter_by(user_id=1).all()
            new_interaction_count = len(new_interactions)
            self.assertEqual(new_interaction_count, interaction_count - 1)
    
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

    def test_invalid_like_count_action(self):
        with app.app_context():
            # Retrieve the test car from the database
            car1 = Car.query.first()
            self.assertIsNotNone(car1, "Car 1 not found in database")

            # Save the car ID and like count for the test
            car1_id = car1.id
            before_decrement = car1.like_count

            # Simulate the invalid AJAX call JSON response
            response = self.app.post(
                f'/toggle_count/{car1_id}', json={'liked': None})
            data = response.get_json()
            self.assertEqual(response.status_code, 400)
            self.assertNotEqual(list(data.keys())[0], 'liked')

            # Re-query the car to get the unchanged like count
            car1 = db.session.get(Car, 1)
            self.assertEqual(car1.like_count, before_decrement)

    
    def test_cards_depleted(self):
        with app.app_context():
            # Simulate a valid 'cards depleted' signal
            base_data = {'isEmpty': True}

            response = self.app.post(
                '/cards-depleted', 
                json=base_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['message'], "No more cards available")


            # Simulate another valid 'cards not depleted' signal
            cards_full_data = base_data.copy()
            cards_full_data['isEmpty'] = False
            response = self.app.post(
                '/cards-depleted', 
                json=cards_full_data
            )
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertEqual(data['message'], "Cards still available")

            # Simulate an invalid 'cards depleted' signal
            invalid_card_data = base_data.copy()
            invalid_card_data.clear()
            response = self.app.post(
                '/cards-depleted', 
                json=invalid_card_data
            )
            self.assertEqual(response.status_code, 400)
            data = response.get_json()
            self.assertEqual(data['error'], "Invalid request")
    """



    """
    def test_reaction_validation(self):
        # Log in the test user
        self.login_test_user()

        with app.app_context():
            # Valid data
            base_data = {'carID': 1, 'swiped_right': True}
            response = self.app.post('/react', json=base_data)
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', response.get_json()['status'])

            # Invalid data (empty)
            empty_reaction_data = base_data.copy()
            empty_reaction_data.clear()
            response = self.app.post('/react', json=empty_reaction_data)
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid car ID and swiped_right provided',
                          response.get_json()['status'])

            # Invalid data (missing car ID)
            invalid_car_id = base_data.copy()            
            invalid_car_id['carID'] = None
            response = self.app.post(
                '/react', json=invalid_car_id)
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid car ID provided',
                          response.get_json()['status'])

            # Invalid data (missing swiped_right)
            invalid_swipe_action = base_data.copy()     
            invalid_swipe_action['swiped_right'] = None       
            response = self.app.post('/react', json=invalid_swipe_action)
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid swiped_right provided',
                          response.get_json()['status'])

    
    # Mocking a database error
    def test_database_error(self):
        with app.app_context():
            with patch('app.views.db.session.commit') as mock_commit:
                mock_commit.side_effect = IntegrityError('', '', '')
                response = self.app.post(
                    '/react', json={'carID': 1, 'swiped_right': True})
                self.assertEqual(response.status_code, 500)
                self.assertIn('error', response.get_json()['status'])
    
    
    

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

