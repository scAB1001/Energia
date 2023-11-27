from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from . import db

HASH_TYPE = 'pbkdf2:sha256'  # 'scrypt'

def authenticate_user(email, password):
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return user
    return None


def create_user(email, first_name, password):
    hashed_password = generate_password_hash(password, method=HASH_TYPE)
    new_user = User(email=email, first_name=first_name,
                    password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return new_user


def migrate_password(user, password, hash_type=HASH_TYPE):
    if not user.password.startswith(HASH_TYPE) and check_password_hash(user.password, password):
        user.password = generate_password_hash(password, method=hash_type)
        db.session.commit()


