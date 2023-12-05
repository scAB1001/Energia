# test.py
import unittest
import os
from . import db, models

basedir = os.path.abspath(os.path.dirname(__file__))

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
            os.path.join(basedir, 'test.db')
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
        response = self.app.get(
            '/this-route-does-not-exist', follow_redirects=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Page Not Found', response.data)



if __name__ == '__main__':
    unittest.main()
