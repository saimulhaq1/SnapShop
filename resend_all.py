from app import create_app
from app.extensions import db
from app.models.customer_model import Customer
from app.controllers.register_forget import send_verification_email

app = create_app()
with app.app_context():
    users = Customer.query.filter_by(status='INACTIVE').all()
    print("--- Resending to Inactive Users ---")
    for u in users:
        print(f"Resending to ID: {u.customer_id}, Email: {u.email}")
        try:
            success = send_verification_email(u)
            print(f"   -> Success: {success}")
            print(f"   -> New Token: {u.verify_token}")
        except Exception as e:
            print(f"   -> Error: {e}")
