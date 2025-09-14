import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app import db
from models.User import User
from models.restaurant import Restaurant, Table
from models.booking import Booking
from datetime import datetime, date

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def dashboard():
    """Admin dashboard"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    # Get statistics
    total_users = User.query.count()
    total_restaurants = Restaurant.query.count()
    total_bookings = Booking.query.count()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', 
                         total_users=total_users,
                         total_restaurants=total_restaurants, 
                         total_bookings=total_bookings,
                         recent_bookings=recent_bookings)

@admin_bp.route('/users')
def users():
    """Manage users"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/restaurants')
def restaurants():
    """Manage restaurants"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    restaurants = Restaurant.query.all()
    return render_template('admin/restaurants.html', restaurants=restaurants)

@admin_bp.route('/bookings')
def bookings():
    """Manage all bookings"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=bookings)

@admin_bp.route('/restaurant/add', methods=['GET', 'POST'])
def add_restaurant():
    """Add new restaurant"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    if request.method == 'POST':
        # Create new restaurant
        restaurant = Restaurant(
            name=request.form['name'],
            description=request.form.get('description', ''),
            address=request.form['address'],
            city=request.form['city'],
            state=request.form.get('state', ''),
            zip_code=request.form.get('zip_code', ''),
            phone=request.form.get('phone', ''),
            email=request.form.get('email', ''),
            cuisine_type=request.form.get('cuisine_type', ''),
            price_range=request.form.get('price_range', '$'),
            total_capacity=int(request.form.get('total_capacity', 0))
        )
        
        try:
            db.session.add(restaurant)
            db.session.commit()
            flash('Restaurant added successfully!', 'success')
            return redirect(url_for('admin.restaurants'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to add restaurant. Please try again.', 'error')
    
    return render_template('admin/add_restaurant.html')

@admin_bp.route('/user/<int:user_id>/toggle-status')
def toggle_user_status(user_id):
    """Toggle user active status"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    
    try:
        db.session.commit()
        status = "activated" if user.is_active else "deactivated"
        flash(f'User {user.username} has been {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update user status.', 'error')
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/booking/<int:booking_id>/update-status', methods=['POST'])
def update_booking_status(booking_id):
    """Update booking status"""
    if session.get('role') != 'admin':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form['status']
    
    booking.status = new_status
    
    try:
        db.session.commit()
        flash(f'Booking status updated to {new_status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update booking status.', 'error')
    
    return redirect(url_for('admin.bookings'))