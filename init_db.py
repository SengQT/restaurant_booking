from app import create_app, db
from models.User import User
from models.restaurant import Restaurant, Table
from models.booking import Booking
from datetime import datetime, time, date

def init_database():
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate them
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        
        # Create sample users
        print("Creating users...")
        admin = User(
            username='admin',
            email='admin@restaurant.com',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        
        manager = User(
            username='manager',
            email='manager@restaurant.com',
            password='manager123',
            first_name='Manager',
            last_name='User',
            role='manager'
        )
        
        customer = User(
            username='customer',
            email='customer@example.com',
            password='customer123',
            first_name='John',
            last_name='Doe',
            phone='123-456-7890'
        )
        
        db.session.add_all([admin, manager, customer])
        db.session.commit()
        print("✅ Users created successfully!")
        
        # Create sample restaurants
        print("Creating restaurants...")
        restaurant1 = Restaurant(
            name="Sample Restaurant",
            description="A wonderful dining experience",
            address="123 Main St",
            city="Sample City",
            state="Sample State",
            zip_code="12345",
            phone="555-0123",
            email="info@samplerestaurant.com",
            cuisine_type="Italian",
            price_range="$$",
            total_capacity=50,
            opening_time=time(11, 0),
            closing_time=time(22, 0)
        )
        
        restaurant2 = Restaurant(
            name="Fine Dining Palace",
            description="Exquisite culinary experience",
            address="456 Luxury Ave",
            city="Sample City",
            state="Sample State",
            zip_code="12345",
            phone="555-0456",
            email="info@finedining.com",
            cuisine_type="French",
            price_range="$$$$",
            total_capacity=30,
            opening_time=time(17, 0),
            closing_time=time(23, 0)
        )
        
        db.session.add_all([restaurant1, restaurant2])
        db.session.commit()
        print("✅ Restaurants created successfully!")
        
        # Create tables for restaurants
        print("Creating tables...")
        tables_r1 = [
            Table(restaurant_id=restaurant1.id, table_number='T1', capacity=2),
            Table(restaurant_id=restaurant1.id, table_number='T2', capacity=4),
            Table(restaurant_id=restaurant1.id, table_number='T3', capacity=4),
            Table(restaurant_id=restaurant1.id, table_number='T4', capacity=6),
            Table(restaurant_id=restaurant1.id, table_number='T5', capacity=8),
        ]
        
        tables_r2 = [
            Table(restaurant_id=restaurant2.id, table_number='T1', capacity=2),
            Table(restaurant_id=restaurant2.id, table_number='T2', capacity=4),
            Table(restaurant_id=restaurant2.id, table_number='T3', capacity=6),
        ]
        
        all_tables = tables_r1 + tables_r2
        db.session.add_all(all_tables)
        db.session.commit()
        print("✅ Tables created successfully!")
        
        # Create sample bookings
        print("Creating sample bookings...")
        booking1 = Booking(
            user_id=customer.id,
            restaurant_id=restaurant1.id,
            table_id=tables_r1[0].id,
            booking_date=date(2024, 12, 25),
            booking_time=time(19, 0),
            party_size=2,
            customer_name=f"{customer.first_name} {customer.last_name}",
            customer_phone=customer.phone,
            customer_email=customer.email,
            status='confirmed',
            special_requests='Window table preferred'
        )
        
        booking2 = Booking(
            user_id=customer.id,
            restaurant_id=restaurant2.id,
            table_id=tables_r2[1].id,
            booking_date=date(2024, 12, 31),
            booking_time=time(20, 0),
            party_size=4,
            customer_name=f"{customer.first_name} {customer.last_name}",
            customer_phone=customer.phone,
            customer_email=customer.email,
            status='pending',
            special_requests='Anniversary dinner'
        )
        
        db.session.add_all([booking1, booking2])
        db.session.commit()
        print("✅ Sample bookings created successfully!")
        
        print("\n" + "🎉" * 25)
        print("DATABASE INITIALIZED SUCCESSFULLY!")
        print("🎉" * 25)
        print("\n👥 Default users created:")
        print("🔑 Admin: admin / admin123")
        print("👨‍💼 Manager: manager / manager123")
        print("👤 Customer: customer / customer123")
        print("\n🍽️ Restaurants created:")
        print("🍝 Sample Restaurant (Italian, $$)")
        print("🥂 Fine Dining Palace (French, $$$$)")
        print("\n📊 Database Statistics:")
        print(f"👥 Users: {User.query.count()}")
        print(f"🏢 Restaurants: {Restaurant.query.count()}")
        print(f"🪑 Tables: {Table.query.count()}")
        print(f"📅 Bookings: {Booking.query.count()}")
        print("\n💾 Database file: restaurant.db")

if __name__ == '__main__':
    init_database()