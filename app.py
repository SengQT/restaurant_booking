from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import the shared SQLAlchemy instance
from db import db

def create_app():
    # Create Flask app instance
    app = Flask(__name__)

    # --- Configuration ---
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///restaurant.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # --- Initialize Extensions ---
    db.init_app(app)
    Migrate(app, db)

    # --- Import Models ---
    # These imports must come after db.init_app(app)
    from models.User import User
    from models.restaurant import Restaurant, Table
    from models.booking import Booking

    # --- Register Blueprints ---
    from routes.User import user_bp
    from routes.admin import admin_bp
    from routes.manager import manager_bp

    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')

    return app

# --- Entry Point ---
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)