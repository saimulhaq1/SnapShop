from app import create_app
from app.extensions import db
from app.models.customer_model import Customer

app = create_app()
with app.app_context():
    users = Customer.query.all()
    print("--- User List ---")
    for u in users:
        print(f"ID: {u.customer_id}, Email: {u.email}, Status: {u.status}")
