from app.extensions import db
from .enums import OrderStatus

class SalesOrder(db.Model):
    __tablename__ = 'sales_order'
    
    # MVC Fix: Prevents "already defined" errors during reloads
    __table_args__ = {'extend_existing': True}

    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    
    # Using db.func for database-level timestamps
    order_date = db.Column(db.DateTime, default=db.func.current_timestamp())
    total_amount = db.Column(db.Numeric(12, 2), nullable=False) 
    total_paid = db.Column(db.Numeric(12, 2), default=0.00)
    delivery_date = db.Column(db.DateTime, nullable=True)
    
    # Defaulting to PENDING to match your checkout flow
    status = db.Column(db.Enum(OrderStatus, name='order_status_enum'), default=OrderStatus.PENDING, nullable=False)
    is_revenue_tracked = db.Column(db.Boolean, default=False)

    # --- MVC Relationships ---
    
    # Linked to Address.orders
    address_link = db.relationship('Address', back_populates='orders')
    
    # FIXED: Added mutual back_populates and broader overlaps to silence warnings
    # This matches the relationship in the Customer model
    customer_link = db.relationship(
        'Customer', 
        back_populates='orders', 
        overlaps="customer,orders,customer_link"
    )
    
    # Links to Order Items
    order_items = db.relationship('SalesOrderItem', back_populates='order', lazy=True, cascade="all, delete-orphan")
    
    # Links to Payments
    payments = db.relationship('Payment', backref='order', lazy=True)

    # --- MVC Logic: Smart Model Methods ---

    def mark_as_cancelled(self):
        """MVC Logic: Encapsulated return/cancel process to restore stock."""
        if self.status != OrderStatus.CANCELLED:
            for item in self.order_items:
                if item.product:
                    # Logic assumes Product model has a restore_stock method
                    item.product.stock += item.quantity 
            self.status = OrderStatus.CANCELLED
            db.session.add(self)

    def __repr__(self):
        return f"<SalesOrder #{self.order_id} - Status: {self.status.name}>"