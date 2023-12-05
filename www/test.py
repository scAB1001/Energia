# import os
import unittest
from flask import Flask, session
from app import app, db
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from app.models import User, Car
from app.auth_service import authenticate_and_login, register_and_login
from app.views import home, explore, saved, single_view, settings, delete_account

#basedir = os.path.abspath(os.path.dirname(__file__))

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()
            # Creating test user and car for authentication and interaction tests
            hashed_password = User.generate_hash('testpassword')
            test_user = User(email='test@example.com',
                             first_name='Test', password=hashed_password)
            db.session.add(test_user)
            test_car = Car(image='test_image', car_name='Test Car', make='Test Make',
                           model='Test Model', year=2021, body_type='Test Type',
                           horsepower=100, monthly_payment=500.0, mileage=10000, like_count=0)
            db.session.add(test_car)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Add all other tests here...

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
            car = Car(image='new_image', car_name='New Car', make='New Make',
                    model='New Model', year=2021, body_type='New Type',
                    horsepower=100, monthly_payment=600.0, mileage=10000, like_count=0)
            db.session.add(car)
            db.session.commit()
            self.assertIsNotNone(car.id)

    def test_valid_car_creation(self):
        with app.app_context():
            car = Car(make='', model='', year=1900, like_count=0)
            db.session.add(car)
            with self.assertRaises(Exception):
                db.session.commit()

    
    def test_like_count_increment(self):
        with app.app_context():
            car = Car(make='Test Make', model='Test Model',
                    year=2021, like_count=0)
            db.session.add(car)
            db.session.commit()
            car.like_count += 1
            db.session.commit()
            self.assertEqual(car.like_count, 1)

    def test_like_count_decrement(self):
        with app.app_context():
            car = Car(make='Test Make', model='Test Model',
                    year=2021, like_count=1)
            db.session.add(car)
            db.session.commit()
            car.like_count -= 1
            db.session.commit()
            self.assertEqual(car.like_count, 0)


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



if __name__ == '__main__':
    unittest.main()

