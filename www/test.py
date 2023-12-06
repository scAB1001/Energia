import os, unittest, json
from flask import Flask, session
from app import app, db
from flask_login import login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from app.models import User, Car
from app.auth_service import generate_hash, validate_password, authenticate_and_login, create_user, register_and_login
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
                print("Test database created successfully.")

            self._create_test_data()

    def _create_test_data(self):
        # Creating valid test user and car for authentication and interaction tests
        test_user = User(
            email='sc222ab@mail.com', first_name='Andreas',
            password=generate_hash('password123'))
        db.session.add(test_user)

        test_car = Car(
            image='ferrariF512TR3', car_name='Ferrari F512 TR', make='Ferrari',
            model='F512 TR', year=1991, body_type='2-door berlinetta', horsepower=422,
            monthly_payment=3245.32, mileage=198978, like_count=11)

        db.session.add(test_car)
        db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


    def test_home_page_loads(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_404_page(self):
        response = self.app.get(
            '/this-route-does-not-exist', follow_redirects=True)
        self.assertEqual(response.status_code, 404)

    # Model Tests
    def test_valid_car_creation(self):
        with app.app_context():
            test_car_id = db.session.get(Car, 1).id
            self.assertIsNotNone(test_car_id)


    def test_invalid_car_creation(self):
        with app.app_context():
            test_car = Car(make='', model='', year=1900, like_count=0)
            db.session.add(test_car)
            with self.assertRaises(Exception):
                db.session.commit()
            self.assertIsNone(test_car.id)

    
    def test_like_count_increment(self):
        with app.app_context():
            # Retrieve the test car from the database (entry 1)
            test_car = Car.query.first()
            self.assertIsNotNone(test_car, "Test car not found in database")

            # Save the car ID and like count for the test
            test_car_id = test_car.id
            before_increment = test_car.like_count

            # Simulate the AJAX call to increment like count
            response = self.app.post(f'/toggle_count/{test_car_id}', json={'liked': True})
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['like_count'], before_increment + 1)

            # Re-query the car to get the updated like count
            test_car = db.session.get(Car, 1)
            self.assertEqual(test_car.like_count, before_increment + 1)

    def test_like_count_decrement(self):
        with app.app_context():
            # Retrieve the test car from the database
            test_car = Car.query.first()
            self.assertIsNotNone(test_car, "Test car not found in database")

            # Save the car ID and like count for the test
            test_car_id = test_car.id
            before_decrement = test_car.like_count

            # Simulate the AJAX call to increment like count
            response = self.app.post(
                f'/toggle_count/{test_car_id}', json={'liked': False})
            data = response.get_json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['like_count'], before_decrement - 1)

            # Re-query the car to get the updated like count
            test_car = db.session.get(Car, 1)
            self.assertEqual(test_car.like_count, before_decrement - 1)

"""
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

