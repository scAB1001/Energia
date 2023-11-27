from app import db
from sqlalchemy.sql import func
from flask_login import UserMixin

DT = func.now()

class BaseModel(db.Model):
    """
    Base class for SQLAlchemy models that includes common columns.

    Attributes:
        id (int): Primary key column.
        created_at (datetime): Creation timestamp
        updated_at (datetime): Update timestamp
    """
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, nullable=False)  # Primary key column
    created_at = db.Column(db.DateTime(timezone=True), default=DT)  # Creation timestamp
    updated_at = db.Column(db.DateTime(timezone=True), default=DT, onupdate=DT)  # Update timestamp


class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    # Existing fields
    email = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    first_name = db.Column(db.String(20), nullable=False)

    # Define relationships
    leases = db.relationship('Lease', backref='user', lazy=True)
    interactions = db.relationship(
        'UserInteraction', backref='user', lazy=True)

    def __repr__(self):
        return f"ID:{self.id}  {self.first_name}, {self.email}, {self.password}"


class Car(BaseModel):
    __tablename__ = 'cars'

    image = db.Column(db.String(255), unique=True, nullable=False)
    car_name = db.Column(db.String(255), unique=True, nullable=False)
    make = db.Column(db.String(255), nullable=False)
    model = db.Column(db.String(255), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    body_type = db.Column(db.String(255), nullable=False)
    horsepower = db.Column(db.Integer, nullable=False)
    monthly_payment = db.Column(db.Float, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)

    leases = db.relationship('Lease', backref='car', lazy=True)
    interactions = db.relationship('UserInteraction', backref='car', lazy=True)

    # Summary details
    def __repr__(self):
        return f"Car {self.id}: [{self.make}, {self.model}, {self.year}]"
    
    # Key details for card display
    def card_info(self):
        return {
            'carID': int(str(self.id)),
            'imageUrl': f'{self.image}',
            'carName': f'{self.car_name}',
            'details': f'Price: £{self.monthly_payment}pm\t\tBody: {self.body_type}\nHorsepower: {self.horsepower}bhp\t\tMake: {self.make}'
        }
    
    # Full details to display in 'Saved (single_view)' section
    def full_details(self):
        return {
            'imageUrl': f'{self.image}',
            'carName': f'{self.car_name}',
            'make': f'{self.make}',
            'model': f'{self.model}',
            'year': f'{self.year}',
            'body_type': f'{self.body_type}',
            'horsepower': f'{self.horsepower}',
            'monthly_payment': f'{self.monthly_payment}',
            'mileage': f'{self.mileage}'
        }

class Lease(BaseModel):
    __tablename__ = 'leases'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    term_length = db.Column(db.Integer, nullable=False)
    mileage_limit = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Lease [{self.user_id}, {self.car_id}, {self.term_length}]"


class UserInteraction(BaseModel):
    __tablename__ = 'user_interactions'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('cars.id'), nullable=False)
    swiped_right = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), default=DT)

    def __repr__(self):
        return f"UserInteraction: ID:{self.id} [userID:{self.user_id}, carID:{self.car_id}, swiped_right:{self.swiped_right}]"

