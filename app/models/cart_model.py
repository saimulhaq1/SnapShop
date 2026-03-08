from app.extensions import db
from datetime import datetime

class Cart(db.Model):
    __tablename__ = 'cart'
    
    cart_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    
    # Updated to 'product.pro_id' to match your Product model
    product_id = db.Column(db.Integer, db.ForeignKey('product.pro_id'), nullable=False)
    
    qty = db.Column(db.Integer, default=1)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', backref='cart_entries')