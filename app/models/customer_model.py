import json
from datetime import datetime
from app.extensions import db
from .enums import CommonStatus, UserRole

class Customer(db.Model):
    __tablename__ = 'customer'
    
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    mobile_no = db.Column(db.String(20))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    bank_name = db.Column(db.String(100), nullable=True)
    bank_account_no = db.Column(db.String(50), nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True, default='default_user.png')
    # --- Auth & Permissions Fields ---
    role = db.Column(db.Enum(UserRole, name='user_role_enum'), default=UserRole.CUSTOMER, nullable=False)
    total_spent = db.Column(db.Numeric(12, 2), default=0.00)
    
    # Stores permissions as a JSON string (e.g., '{"hide_profit": true}')
    permissions = db.Column(db.Text, default='{}')
    
    # Self-referencing foreign key: tracks which admin created this employee
    created_by = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=True)
    
    join_date = db.Column(db.DateTime, default=datetime.utcnow)
    verify_token = db.Column(db.String(255))
    verify_expiry = db.Column(db.DateTime)
    verify_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(CommonStatus, name='common_status_enum'), default=CommonStatus.ACTIVE)

    # Related tables for Reviews
    reviews = db.relationship('ProductReview', back_populates='author', lazy=True, cascade='all, delete-orphan')
    
    # Related Notifications
    notifications = db.relationship('Notification', back_populates='customer', lazy='dynamic', cascade='all, delete-orphan')
    
    # --- Relationships ---
    addresses = db.relationship('Address', backref='customer', lazy=True)
    orders = db.relationship('SalesOrder', backref='customer', lazy=True)
    
    # Relationship to access the creator's info: employee.creator.name
    creator = db.relationship('Customer', remote_side=[customer_id], backref='created_employees')

    def get_permissions(self):
        """Helper to convert the JSON string back into a Python dictionary."""
        try:
            # If permissions is already a dict (some DB drivers do this), return it
            if isinstance(self.permissions, dict):
                return self.permissions
            return json.loads(self.permissions) if self.permissions else {}
        except (ValueError, TypeError):
            return {}

    def __repr__(self):
        return f"<Customer {self.name} ({self.role})>"