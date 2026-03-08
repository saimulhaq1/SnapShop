from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.session.execute(db.text("ALTER TABLE sales_order ADD COLUMN is_revenue_tracked BOOLEAN DEFAULT FALSE"))
        db.session.commit()
        print("Success: Added is_revenue_tracked column.")
    except Exception as e:
        print(f"Error: {e}")
