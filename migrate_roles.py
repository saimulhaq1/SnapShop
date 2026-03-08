from app import create_app, db

app = create_app()
with app.app_context():
    # Update Customer Roles
    print("Migrating UserRoles...")
    # First, need to modify column if it's an ENUM
    db.session.execute(db.text("ALTER TABLE customer MODIFY COLUMN role VARCHAR(50)"))
    db.session.execute(db.text("UPDATE customer SET role = 'CUSTOMER' WHERE role = 'customer'"))
    db.session.execute(db.text("UPDATE customer SET role = 'ADMIN' WHERE role = 'admin'"))
    db.session.execute(db.text("UPDATE customer SET role = 'STAFF' WHERE role = 'staff'"))
    
    # Re-apply ENUM
    db.session.execute(db.text("ALTER TABLE customer MODIFY COLUMN role ENUM('CUSTOMER', 'ADMIN', 'STAFF') DEFAULT 'CUSTOMER'"))
    db.session.commit()
    print("UserRole Migration complete.")
