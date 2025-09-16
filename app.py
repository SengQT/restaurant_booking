import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import uuid
from functools import wraps
# Import database and models
from db import db
from models.user import User       # match the filename exactly
from models.restaurant import Restaurant
from models.booking import Booking

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'devkey')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize db
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        # Create default admin if not exists
        admin = User.query.filter_by(email='admin@restaurant.com').first()
        if not admin:
            admin_user = User(
                email='admin@restaurant.com',
                username='admin',
                password=generate_password_hash('admin123'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
    
    # Helper function to check allowed file extensions
    def allowed_file(filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    # Authentication decorators
    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def admin_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            current_user = User.query.get(session['user_id'])
            if not current_user or current_user.role not in ['admin', 'manager']:
                flash('Access denied. Admin or Manager privileges required.', 'error')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    
    # Routes
    @app.route('/')
    def index():
        restaurants = Restaurant.query.all()
        return render_template('user/index.html', restaurants=restaurants)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            found_user = User.query.filter_by(email=email).first()
            
            if found_user and check_password_hash(found_user.password, password):
                session['user_id'] = found_user.id
                session['username'] = found_user.username
                session['role'] = found_user.role
                
                flash('Login successful!', 'success')
                if found_user.role in ['admin', 'manager']:
                    return redirect(url_for('admin_dashboard'))
                else:
                    return redirect(url_for('user_dashboard'))
            else:
                flash('Invalid email or password', 'error')
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            email = request.form['email']
            username = request.form['username']
            password = request.form['password']
            
            if User.query.filter_by(email=email).first():
                flash('Email already registered', 'error')
                return render_template('register.html')
            
            if User.query.filter_by(username=username).first():
                flash('Username already taken', 'error')
                return render_template('register.html')
            
            new_user = User(
                email=email,
                username=username,
                password=generate_password_hash(password),
                role='user'
            )
            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    @app.route('/logout')
    def logout():
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/user/dashboard')
    @login_required
    def user_dashboard():
        current_user = User.query.get(session['user_id'])
        if current_user is None:
            session.clear()
            flash('Your session is invalid. Please log in again.', 'error')
            return redirect(url_for('login'))
        
        bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
        return render_template('user/dashboard.html', user=current_user, bookings=bookings)
    
    @app.route('/book/<int:restaurant_id>', methods=['GET', 'POST'])
    @login_required
    def book_restaurant(restaurant_id):
        restaurant = Restaurant.query.get_or_404(restaurant_id)
        
        if request.method == 'POST':
            booking_date_raw = request.form['booking_date'].strip()
            booking_time_raw = request.form['booking_time'].strip()
            guests_raw = request.form['guests'].strip()
            special_requests = request.form.get('special_requests', '')

            # --- Parse date (accepts dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd) ---
            booking_date = None
            for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
                try:
                    booking_date = datetime.strptime(booking_date_raw, fmt).date()
                    break
                except ValueError:
                    continue
            if booking_date is None:
                flash("Invalid date format. Please use DD/MM/YYYY.", "error")
                return redirect(url_for('book_restaurant', restaurant_id=restaurant_id))

            # --- Parse time (HH:MM 24-hour) ---
            try:
                booking_time = datetime.strptime(booking_time_raw, "%H:%M").time()
            except ValueError:
                flash("Invalid time format. Please use HH:MM (24-hour).", "error")
                return redirect(url_for('book_restaurant', restaurant_id=restaurant_id))

            # --- Parse guests (must be a number) ---
            try:
                guests = int(guests_raw)
                if guests <= 0:
                    raise ValueError
            except ValueError:
                flash("Guests must be a positive number.", "error")
                return redirect(url_for('book_restaurant', restaurant_id=restaurant_id))

            # Save booking
            booking = Booking(
                user_id=session['user_id'],
                restaurant_id=restaurant_id,
                booking_date=booking_date,
                booking_time=booking_time,
                guests=guests,
                special_requests=special_requests
            )
            db.session.add(booking)
            db.session.commit()

            flash('Booking successful! Your booking is pending confirmation.', 'success')
            return redirect(url_for('user_dashboard'))
        
        return render_template('user/booking.html', restaurant=restaurant)

    
    @app.route('/admin')
    @admin_required
    def admin_dashboard():
        restaurants = Restaurant.query.all()
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        users = User.query.all()
        return render_template('admin/dashboard.html', 
                             restaurants=restaurants, 
                             bookings=bookings, 
                             users=users)
    
    @app.route('/admin/restaurants/add', methods=['GET', 'POST'])
    @admin_required
    def add_restaurant():
        if request.method == 'POST':
            name = request.form['name']
            description = request.form['description']
            location = request.form['location']
            phone = request.form['phone']
            email = request.form['email']
            capacity = int(request.form['capacity'])
            
            image_filename = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = str(uuid.uuid4()) + '_' + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    image_filename = filename
            
            restaurant = Restaurant(
                name=name,
                description=description,
                location=location,
                phone=phone,
                email=email,
                capacity=capacity,
                image=image_filename
            )
            
            db.session.add(restaurant)
            db.session.commit()
            
            flash('Restaurant added successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/add_restaurant.html')
    
    @app.route('/admin/restaurants/edit/<int:id>', methods=['GET', 'POST'])
    @admin_required
    def edit_restaurant(id):
        restaurant = Restaurant.query.get_or_404(id)
        
        if request.method == 'POST':
            restaurant.name = request.form['name']
            restaurant.description = request.form['description']
            restaurant.location = request.form['location']
            restaurant.phone = request.form['phone']
            restaurant.email = request.form['email']
            restaurant.capacity = int(request.form['capacity'])
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filename = str(uuid.uuid4()) + '_' + filename
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    restaurant.image = filename
            
            db.session.commit()
            flash('Restaurant updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin/edit_restaurant.html', restaurant=restaurant)
    
    @app.route('/admin/restaurants/delete/<int:id>')
    @admin_required
    def delete_restaurant(id):
        restaurant = Restaurant.query.get_or_404(id)
        db.session.delete(restaurant)
        db.session.commit()
        flash('Restaurant deleted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    @app.route('/admin/bookings')
    @admin_required
    def manage_bookings():
        bookings = Booking.query.order_by(Booking.created_at.desc()).all()
        return render_template('admin/booking.html', bookings=bookings)
    
    @app.route('/admin/booking/status/<int:id>/<status>')
    @admin_required
    def update_booking_status(id, status):
        booking = Booking.query.get_or_404(id)
        if status in ['confirmed', 'cancelled']:
            booking.status = status
            db.session.commit()
            flash(f'Booking {status} successfully!', 'success')
        return redirect(url_for('manage_bookings'))
    
    # Add datetime and timedelta to template context
    @app.template_global()
    def datetime_now():
        return datetime.now()
    
    @app.template_global() 
    def timedelta_days(days):
        return timedelta(days=days)
    
    return app
app = create_app()
if __name__ == '__main__':

    app.run(debug=True)
