from app import app, db
import models

with app.app_context():
    print("Checking database structure...")
    # This creates any tables that are missing in MySQL 
    # but defined in your models.py
    db.create_all()
    print("✅ All tables (including tax_rate and country) have been created!")
    
    # Stamp the migration so Flask-Migrate knows we are up to date
    try:
        from flask_migrate import stamp
        stamp()
        print("✅ Migration stamp updated to 'head'.")
    except Exception as e:
        print("Could not stamp, but tables are created.")
        