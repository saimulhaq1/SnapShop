from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.session.execute(db.text("ALTER TABLE sales_order ADD COLUMN total_paid DECIMAL(12,2) DEFAULT 0.00"))
        db.session.commit()
        print("Success: Added total_paid column.")
    except Exception as e:
        print(f"Error: {e}")
