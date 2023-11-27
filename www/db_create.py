from config import SQLALCHEMY_DATABASE_URI
from app import db
import os.path

# OG
#with app.app_context():
#    db.create_all()

# Checks if the database file already exists before attempting to create it, ensuring it's safe to run multiple times.
if __name__ == '__main__':
    db_file = os.path.join(os.path.dirname(__file__), 'app.db')
    if not os.path.exists(db_file):
        with app.app_context():
            db.create_all()
            print("Database created.")
    else:
        print("Database already exists.")
