from app import create_app, db
from app.models import ProductReview
app = create_app()
with app.app_context():
    print("Modifying product_review table...")
    try:
        db.session.execute(db.text("ALTER TABLE product_review ADD COLUMN verified_purchase BOOLEAN DEFAULT FALSE"))
        db.session.commit()
        print("Success: Added verified_purchase column.")
    except Exception as e:
        print(f"Error: {e}")
