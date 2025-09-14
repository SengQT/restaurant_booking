from db import db
from datetime import datetime

class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurants.id'), nullable=False)
    table_id = db.Column(db.Integer, db.ForeignKey('tables.id'), nullable=True)
    
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    party_size = db.Column(db.Integer, nullable=False)
    duration_hours = db.Column(db.Integer, default=2)
    
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    customer_email = db.Column(db.String(100))
    
    status = db.Column(db.String(20), default='pending')
    special_requests = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Simple relationships without conflicts
    user = db.relationship('User', backref='user_bookings')
    restaurant = db.relationship('Restaurant', backref='restaurant_bookings')
    table = db.relationship('Table', backref='table_bookings')
    
    def __repr__(self):
        return f'<Booking {self.id} for {self.customer_name}>'