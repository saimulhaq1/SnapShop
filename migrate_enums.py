from app import create_app, db

app = create_app()
with app.app_context():
    print("Modifying column types to VARCHAR...")
    db.session.execute(db.text("ALTER TABLE sales_order MODIFY COLUMN status VARCHAR(50)"))
    db.session.execute(db.text("ALTER TABLE payment MODIFY COLUMN status VARCHAR(50)"))
    db.session.execute(db.text("ALTER TABLE product MODIFY COLUMN status VARCHAR(50)"))
    
    print("Migrating SalesOrder...")
    db.session.execute(db.text("UPDATE sales_order SET status = 'DELIVERED' WHERE status = 'COMPLETED'"))
    db.session.execute(db.text("UPDATE sales_order SET status = 'PROCESSING' WHERE status = 'ACTIVE'"))
    
    print("Migrating Payment...")
    db.session.execute(db.text("UPDATE payment SET status = 'PAID' WHERE status = 'COMPLETED'"))
    db.session.execute(db.text("UPDATE payment SET status = 'UNPAID' WHERE status = 'PENDING'"))
    db.session.execute(db.text("UPDATE payment SET status = 'FAILED' WHERE status = 'DECLINED'"))
    
    # Wait, the column constraints exist. Let's convert them to ENUM again.
    print("Re-applying ENUM constraints...")
    db.session.execute(db.text("ALTER TABLE sales_order MODIFY COLUMN status ENUM('PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED') DEFAULT 'PENDING'"))
    db.session.execute(db.text("ALTER TABLE payment MODIFY COLUMN status ENUM('UNPAID', 'PARTIAL', 'PAID', 'REFUNDED', 'FAILED') DEFAULT 'UNPAID'"))
    db.session.execute(db.text("ALTER TABLE product MODIFY COLUMN status ENUM('ACTIVE', 'INACTIVE', 'ARCHIVED', 'OUT_OF_STOCK') DEFAULT 'ACTIVE'"))
    
    db.session.commit()
    print("Database migration complete.")
