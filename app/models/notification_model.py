from app.extensions import db

class Notification(db.Model):
    __tablename__ = 'notification'
    
    id = db.Column(db.Integer, primary_key=True)
    # user_id is the recipient. If null, it's a broadcast to everyone.
    user_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=True) 
    
    # role limit e.g., 'ADMIN', 'CUSTOMER', 'ALL'
    recipient_role = db.Column(db.String(20), default='CUSTOMER')
    
    type = db.Column(db.String(50), nullable=False) # e.g., ORDER, REVIEW, BROADCAST
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True) # URL to click
    
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    # Relationships
    customer = db.relationship('Customer', back_populates='notifications')
