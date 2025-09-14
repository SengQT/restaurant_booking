import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from app import db
from models.User import User
from models.restaurant import Restaurant, Table
from models.booking import Booking
from datetime import datetime, date

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/')
def dashboard():
    """Manager dashboard"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    # Get today's bookings
    today = date.today()
    todays_bookings = Booking.query.filter_by(booking_date=today).all()
    pending_bookings = Booking.query.filter_by(status='pending').all()
    
    return render_template('manager/dashboard.html', 
                         todays_bookings=todays_bookings,
                         pending_bookings=pending_bookings)

@manager_bp.route('/bookings')
def bookings():
    """View all bookings"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    bookings = Booking.query.order_by(Booking.booking_date.desc(), Booking.booking_time.desc()).all()
    return render_template('manager/bookings.html', bookings=bookings)

@manager_bp.route('/booking/<int:booking_id>/confirm')
def confirm_booking(booking_id):
    """Confirm a booking"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    booking = Booking.query.get_or_404(booking_id)
    
    # Find suitable table
    suitable_tables = Table.query.filter(
        Table.restaurant_id == booking.restaurant_id,
        Table.capacity >= booking.party_size,
        Table.is_available == True
    ).all()
    
    if suitable_tables:
        booking.table_id = suitable_tables[0].id
        booking.status = 'confirmed'
        
        try:
            db.session.commit()
            flash(f'Booking confirmed! Table {suitable_tables[0].table_number} assigned.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Failed to confirm booking.', 'error')
    else:
        flash('No suitable tables available for this booking.', 'error')
    
    return redirect(url_for('manager.bookings'))

@manager_bp.route('/booking/<int:booking_id>/cancel')
def cancel_booking(booking_id):
    """Cancel a booking"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    booking = Booking.query.get_or_404(booking_id)
    booking.status = 'cancelled'
    
    try:
        db.session.commit()
        flash('Booking cancelled.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Failed to cancel booking.', 'error')
    
    return redirect(url_for('manager.bookings'))

@manager_bp.route('/tables')
def tables():
    """Manage tables"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    restaurants = Restaurant.query.all()
    tables = Table.query.all()
    return render_template('manager/tables.html', restaurants=restaurants, tables=tables)

@manager_bp.route('/table/<int:table_id>/toggle-availability')
def toggle_table_availability(table_id):
    """Toggle table availability"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    table = Table.query.get_or_404(table_id)
    table.is_available = not table.is_available
    
    try:
        db.session.commit()
        status = "available" if table.is_available else "unavailable"
        flash(f'Table {table.table_number} is now {status}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Failed to update table availability.', 'error')
    
    return redirect(url_for('manager.tables'))

@manager_bp.route('/reports')
def reports():
    """View reports"""
    if session.get('role') not in ['manager', 'admin']:
        flash('Access denied. Manager privileges required.', 'error')
        return redirect(url_for('user.index'))
    
    # Get some basic statistics
    total_bookings = Booking.query.count()
    confirmed_bookings = Booking.query.filter_by(status='confirmed').count()
    pending_bookings = Booking.query.filter_by(status='pending').count()
    cancelled_bookings = Booking.query.filter_by(status='cancelled').count()
    
    return render_template('manager/reports.html',
                         total_bookings=total_bookings,
                         confirmed_bookings=confirmed_bookings,
                         pending_bookings=pending_bookings,
                         cancelled_bookings=cancelled_bookings)