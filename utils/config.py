from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from utils.config import Config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models (must be after db initialization)
    from models import user, booking, restaurant
    
    # Register blueprints
    from routes.user import user_bp
    from routes.admin import admin_bp
    from routes.manager import manager_bp
    
    app.register_blueprint(user_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(manager_bp, url_prefix='/manager')
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)