import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import db
from datetime import datetime

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50))
    zip_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    cuisine_type = db.Column(db.String(50))
    price_range = db.Column(db.String(20))
    rating = db.Column(db.Float, default=0.0)
    total_capacity = db.Column(db.Integer, default=0)
    opening_time = db.Column(db.Time)
    closing_time = db.Column(db.Time)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Restaurant {self.name}>'

class Table(db.Model):
    __tablename__ = 'tables'
    
    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    table_number = db.Column(db.String(10), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    __table_args__ = (db.UniqueConstraint('restaurant_id', 'table_number'),)
    
    def __repr__(self):
        return f'<Table {self.table_number} at Restaurant {self.restaurant_id}>'