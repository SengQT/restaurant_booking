from db import db
from datetime import datetime

class Restaurant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    capacity = db.Column(db.Integer, default=50)
    image = db.Column(db.String(255))  # Store filename
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with bookings
    bookings = db.relationship('Booking', backref='restaurant', lazy=True, cascade='all, delete-orphan')
    def __repr__(self):
        return f'<Restaurant {self.name}>'
