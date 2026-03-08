from app.extensions import db
from datetime import datetime

class Voucher(db.Model):
    __tablename__ = 'voucher'

    voucher_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    
    # 'Percentage' or 'Fixed'
    discount_type = db.Column(db.String(20), nullable=False)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Optional constraint: Only applies to a specific category
    category_id = db.Column(db.Integer, db.ForeignKey('category.cat_id'), nullable=True)
    
    # Optional constraint: Minimum cart value required
    min_cart_value = db.Column(db.Numeric(10, 2), nullable=True)
    
    start_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    
    # Specific constraints
    new_customer_only = db.Column(db.Boolean, default=False)
    first_order_only = db.Column(db.Boolean, default=False)
    one_time_use = db.Column(db.Boolean, default=True) # Usually vouchers are 1-time per user
    
    # Usage Tracking
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='vouchers')
    usages = db.relationship('VoucherUsage', back_populates='voucher', cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Voucher {self.code} - {self.name}>"

class VoucherUsage(db.Model):
    __tablename__ = 'voucher_usage'
    
    usage_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    voucher_id = db.Column(db.Integer, db.ForeignKey('voucher.voucher_id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.order_id'), nullable=True) # Nullable if used in cart but not yet checked out
    
    used_at = db.Column(db.DateTime, default=datetime.utcnow)
    discount_applied = db.Column(db.Numeric(10, 2), nullable=False)

    # Relationships
    voucher = db.relationship('Voucher', back_populates='usages')
    customer = db.relationship('Customer', backref='voucher_usages')
    order = db.relationship('SalesOrder', backref='voucher_usage')

    def __repr__(self):
        return f"<VoucherUsage User:{self.customer_id} Voucher:{self.voucher_id}>"
