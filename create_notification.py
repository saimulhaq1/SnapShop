from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.create_all()
        print("Success: Notification table created.")
    except Exception as e:
        print(f"Error: {e}")
