import os
import unittest
from flask import Flask
from flask import session
from flask_sqlalchemy import SQLAlchemy
from app import app, db
from app.models import User, Car

#basedir = os.path.abspath(os.path.dirname(__file__))

class BasicTestCase(unittest.TestCase):
    def setUp(self): 
        app.config.from_object('config')
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
        #    os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    # Example test to check if the home page loads
    def test_home_page_loads(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    # Example test to check if a 404 error is handled
    def test_404_page(self):
        response = self.app.get('/this-route-does-not-exist', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"We can't seem to find the page you're looking for.", response.data)

    # Unit Tests for Models
    def test_car_creation(self):
        with app.app_context():
            # Create a Car with valid data
            car = Car(make='Test Make', model='Test Model',
                    year=2021, like_count=0)
            db.session.add(car)
            db.session.commit()
            self.assertIsNotNone(car.id)

            # Attempt to create a Car with invalid data
            # Assuming these are invalid
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


    # Authentication and Authorization Tests
    def test_successful_login(self):
        with app.app_context():
            # Add a user
            user = User(username='testuser', email='test@example.com')
            # Assuming you have a method to hash the password
            user.set_password('testpassword')
            db.session.add(user)
            db.session.commit()

            # Attempt login
            response = self.app.post('/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            }, follow_redirects=True)
            self.assertIn(b'Successfully logged in', response.data)

    def test_unsuccessful_login(self):
        with app.app_context():
            response = self.app.post('/login', data={
                'username': 'testuser',
                'password': 'wrongpassword'
            }, follow_redirects=True)
            self.assertIn(b'Invalid username or password', response.data)

    def test_user_registration(self):
        with app.app_context():
            # Test registration with valid data
            response = self.app.post('/register', data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpassword',
                'confirm': 'newpassword'
            }, follow_redirects=True)
            self.assertIn(b'Registration successful', response.data)

            # Test registration with invalid data
            response = self.app.post('/register', data={
                'username': 'us',  # Assuming this is too short
                'email': 'newuser@example.com',
                'password': 'newpassword',
                'confirm': 'newpassword'
            }, follow_redirects=True)
            self.assertIn(b'Registration failed', response.data)

    def test_logout(self):
        # Assuming there's a user logged in
        response = self.app.get('/logout', follow_redirects=True)
        self.assertIn(b'Logged out', response.data)
        self.assertNotIn('user_id', session)

    # View Functionality Tests
    def test_like_car(self):
        # Assuming you need to be logged in to like a car
        # and there is a 'like_car' view function
        # Add a car and a user to the database first
        response = self.app.post('/like_car/1', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Car liked', response.data)


if __name__ == '__main__':
    unittest.main()
