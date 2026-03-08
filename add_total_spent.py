from app import create_app, db

app = create_app()
with app.app_context():
    try:
        db.session.execute(db.text("ALTER TABLE customer ADD COLUMN total_spent DECIMAL(12,2) DEFAULT 0.00"))
        db.session.commit()
        print("Successfully added total_spent to customer.")
    except Exception as e:
        print(f"Error: {e}")
