import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app import db
from models.User import User
from models.restaurant import Restaurant, Table
from models.booking import Booking
from datetime import datetime, date

user_bp = Blueprint('user', __name__)

@user_bp.route('/')
def index():
    """Home page showing available restaurants"""
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    return render_template('user/index.html', restaurants=restaurants)

@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form.get('phone', '')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('user/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('user/register.html')
        
        # Create new user
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('user.login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'error')
            return render_template('user/register.html')
    
    return render_template('user/register.html')

@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            # Store user session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('user/login.html')

@user_bp.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('user.index'))

@user_bp.route('/restaurants')
def restaurants():
    """List all available restaurants"""
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    return render_template('user/restaurants.html', restaurants=restaurants)

@user_bp.route('/restaurant/<int:restaurant_id>')
def restaurant_detail(restaurant_id):
    """Restaurant detail page"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    tables = Table.query.filter_by(restaurant_id=restaurant_id).all()
    return render_template('user/restaurant_detail.html', restaurant=restaurant, tables=tables)

@user_bp.route('/book/<int:restaurant_id>', methods=['GET', 'POST'])
def book_table(restaurant_id):
    """Book a table at restaurant"""
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    
    if request.method == 'POST':
        # Get form data
        booking_date = datetime.strptime(request.form['booking_date'], '%Y-%m-%d').date()
        booking_time = datetime.strptime(request.form['booking_time'], '%H:%M').time()
        party_size = int(request.form['party_size'])
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        customer_email = request.form.get('customer_email', '')
        special_requests = request.form.get('special_requests', '')
        
        # Get user_id from session (default to 1 if no session)
        user_id = session.get('user_id', 1)
        
        # Create booking
        booking = Booking(
            user_id=user_id,
            restaurant_id=restaurant_id,
            booking_date=booking_date,
            booking_time=booking_time,
            party_size=party_size,
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            special_requests=special_requests,
            status='pending'
        )
        
        try:
            db.session.add(booking)
            db.session.commit()
            flash('Booking request submitted successfully!', 'success')
            return redirect(url_for('user.booking_confirmation', booking_id=booking.id))
        except Exception as e:
            db.session.rollback()
            flash('Booking failed. Please try again.', 'error')
    
    return render_template('user/booking.html', restaurant=restaurant)

@user_bp.route('/booking/<int:booking_id>')
def booking_confirmation(booking_id):
    """Booking confirmation page"""
    booking = Booking.query.get_or_404(booking_id)
    return render_template('user/booking_confirmation.html', booking=booking)

@user_bp.route('/my-bookings')
def my_bookings():
    """User's booking history"""
    user_id = session.get('user_id')
    if user_id:
        bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    else:
        bookings = []
    return render_template('user/my_bookings.html', bookings=bookings)

@user_bp.route('/dashboard')
def dashboard():
    """User dashboard"""
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        recent_bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).limit(5).all()
    else:
        user = None
        recent_bookings = []
    
    return render_template('user/dashboard.html', user=user, bookings=recent_bookings)

@user_bp.route('/api/restaurants')
def api_restaurants():
    """API endpoint for restaurants"""
    restaurants = Restaurant.query.filter_by(is_active=True).all()
    return jsonify([{
        'id': r.id,
        'name': r.name,
        'cuisine_type': r.cuisine_type,
        'price_range': r.price_range,
        'rating': r.rating
    } for r in restaurants])

@user_bp.route('/api/tables/<int:restaurant_id>')
def api_tables(restaurant_id):
    """API endpoint for restaurant tables"""
    tables = Table.query.filter_by(restaurant_id=restaurant_id, is_available=True).all()
    return jsonify([{
        'id': t.id,
        'table_number': t.table_number,
        'capacity': t.capacity
    } for t in tables])