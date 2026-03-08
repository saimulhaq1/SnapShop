from app.extensions import db

class SalesOrderItem(db.Model):
    __tablename__ = 'sales_order_item'
    
    # MVC Fix: Prevents "already defined" errors during reloads
    __table_args__ = {'extend_existing': True}

    orderItem_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.order_id'), nullable=False)
    pro_id = db.Column(db.Integer, db.ForeignKey('product.pro_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Snapshot fields - Critical for historical records
    unit_price = db.Column(db.Numeric(10, 2), nullable=False) 
    tax_rate_at_purchase = db.Column(db.Numeric(5, 2), nullable=False, default=0.00) 
    tax_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00) 

    # --- MVC Relationships ---
    
    # Connects back to SalesOrder.order_items using back_populates
    order = db.relationship('SalesOrder', back_populates='order_items')
    
    # Relationship to get product details (Name, Image, etc.)
    product = db.relationship('Product', backref='order_items')

    def __repr__(self):
        return f"<OrderItem Order:{self.order_id} Product:{self.pro_id} Qty:{self.quantity}>"